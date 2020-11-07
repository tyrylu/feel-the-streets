use crate::entities_query::EntitiesQuery;
use crate::entity::{Entity, BasicEntityInfo};
use crate::entity_relationship_kind::EntityRelationshipKind;
use crate::entities_query_executor::EntitiesQueryExecutor;
use crate::semantic_change::{ListChange, SemanticChange};
use crate::{Error, Result};
use rusqlite::types::ToSql;
use rusqlite::{params, Connection, OpenFlags, Row, NO_PARAMS};
use std::collections::HashMap;
use std::path::PathBuf;
use std::time::Instant;

const INIT_AREA_DB_SQL: &str = include_str!("init_area_db.sql");
const INSERT_ENTITY_SQL: &str = "insert into entities (id, discriminator, geometry, effective_width, data) values (?, ?, geomFromWKB(?, 4326), ?, ?)";
const INSERT_ENTITY_SQL_BUFFERED: &str = "insert into entities (id, discriminator, geometry, effective_width, data) values (?, ?, Buffer(geomFromWKB(?, 4326), 0), ?, ?)";
const INSERT_ENTITY_RELATIONSHIP_SQL: &str =
    "INSERT INTO entity_relationships (parent_id, child_id, kind) VALUES (?, ?, ?)";

#[derive(PartialEq)]
enum ForeignKeyViolationClassification {
    Fatal,
    Retryable,
    NoViolation,
}

fn classify_db_error(err: &rusqlite::Error, child_id: &str) -> ForeignKeyViolationClassification {
    if let rusqlite::Error::SqliteFailure(_, Some(_msg)) = err {
        if child_id.chars().next().unwrap() == 'r' {
            ForeignKeyViolationClassification::Retryable // Only relations can have relations as a child, so it is enough to look at the child id.
        } else {
            ForeignKeyViolationClassification::Fatal
        }
    } else {
        ForeignKeyViolationClassification::NoViolation
    }
}

pub(crate) fn row_to_entity(row: &Row) -> core::result::Result<Entity, rusqlite::Error> {
    Ok(Entity {
        id: row.get_unwrap(0),
        geometry: row.get_unwrap(2),
        discriminator: row.get_unwrap(1),
        data: row.get_unwrap(3),
        effective_width: row.get_unwrap(4),
        parsed_data: None,
    })
}

fn init_extensions(conn: &Connection) -> Result<()> {
    conn.load_extension_enable()?;
    conn.load_extension("mod_spatialite", None)?;
    Ok(())
}

pub struct AreaDatabase {
    pub(crate) conn: Connection,
    deferred_relationship_additions: HashMap<String, String>,
}

impl AreaDatabase {
    fn common_construct(conn: Connection) -> Result<Self> {
        conn.execute("PRAGMA foreign_keys=on", params![])?;
        Ok(Self {
            conn,
            deferred_relationship_additions: HashMap::new(),
        })
    }
    pub fn path_for(area: i64, server_side: bool) -> PathBuf {
        let mut root = if server_side {
            PathBuf::from(".")
        } else {
            let mut appdata_dir = dirs::data_local_dir().expect("No local app data dir");
            appdata_dir.push("feel-the-streets/areas");
            appdata_dir
        };
        root.push(format!("{}.db", area));
        root
    }

    pub fn create(area: i64) -> Result<Self> {
        // We're not, and will not, be using anything which a relatively new sqlite would not support, so, if it can help Fedora in not crashing...
        unsafe {
            rusqlite::bypass_sqlite_version_check();
        }
        let conn = Connection::open(&AreaDatabase::path_for(area, true))?;
        init_extensions(&conn)?;
        conn.execute_batch(INIT_AREA_DB_SQL)?;
        AreaDatabase::common_construct(conn)
    }
    pub fn open_existing(area: i64, server_side: bool) -> Result<Self> {
        unsafe {
            rusqlite::bypass_sqlite_version_check();
        }
        let conn = Connection::open_with_flags(
            &AreaDatabase::path_for(area, server_side),
            OpenFlags::SQLITE_OPEN_READ_WRITE,
        )?;
        init_extensions(&conn)?;
        AreaDatabase::common_construct(conn)
    }

    pub fn insert_entities<T>(&mut self, entities: T) -> Result<()>
    where
        T: Iterator<Item = (Entity, Box<dyn Iterator<Item = String>>)>,
    {
        let mut count = 0;
        self.begin()?;
        let mut deferred_relationship_insertions = HashMap::new();
        for (entity, related_ids) in entities {
            let mut insert_related_stmt =
                self.conn.prepare_cached(INSERT_ENTITY_RELATIONSHIP_SQL)?;
            if entity.geometry.len() < 1_000_000 {
                let mut insert_stmt = if self.geometry_is_valid(&entity.geometry)? {
                    self.conn.prepare(INSERT_ENTITY_SQL)?
                } else {
                    self.conn.prepare(INSERT_ENTITY_SQL_BUFFERED)?
                };
                trace!("Inserting {:?}", entity);
                match insert_stmt.execute(params![
                    entity.id,
                    entity.discriminator,
                    entity.geometry,
                    entity.effective_width,
                    entity.data,
                ]) {
                    Ok(_) => {
                        count += 1;
                        for related_id in related_ids {
                            if let Err(e) =
                                insert_related_stmt.execute(params![entity.id, related_id, EntityRelationshipKind::OSMChild])
                            {
                                match classify_db_error(&e, &related_id) {
                                    ForeignKeyViolationClassification::Retryable => {
                                        deferred_relationship_insertions
                                            .insert(entity.id.clone(), related_id);
                                    }
                                    ForeignKeyViolationClassification::Fatal => {
                                        continue;
                                    } // Now it only means that we tryed to insert a relationship for an entity which we definitely don't have in the database - relations are handled separately and anything else can only depend on a smaller object which was inserted before (because of the overpass API query ordering the entities just right)
                                    ForeignKeyViolationClassification::NoViolation => {
                                        return Err(Error::DbError(e));
                                    }
                                }
                            }
                        }
                    }
                    Err(e) => {
                        error!("Failed to insert entity {:?}, error: {}", entity, e);
                    }
                }
            } else {
                warn!(
                    "Not inserting entity with data {} with geometry size {}.",
                    entity.data,
                    entity.geometry.len()
                )
            }
        }
        // Handle deferred relationship insertions.
        for (parent, child) in deferred_relationship_insertions.iter() {
            self.insert_deferred_entity_relationship(parent, child)?;
        }

        self.commit()?;
        info!("Successfully inserted {} entities.", count);
        Ok(())
    }

    pub fn has_entity(&self, osm_id: &str) -> Result<bool> {
        let mut stmt = self
            .conn
            .prepare_cached("select id from entities where id = ?")?;
        stmt.exists(&[&osm_id]).map_err(Error::from)
    }

    pub fn get_entity(&self, osm_id: &str) -> Result<Option<Entity>> {
        let mut stmt = self.conn.prepare_cached("select id, discriminator, AsBinary(geometry) as geometry, data, effective_width from entities where id = ?")?;
        match stmt.query_row(&[&osm_id], row_to_entity) {
            Ok(e) => Ok(Some(e)),
            Err(e) => match e {
                rusqlite::Error::QueryReturnedNoRows => Ok(None),
                _ => Err(Error::DbError(e)),
            },
        }
    }
    pub fn get_entities(&self, query: &EntitiesQuery) -> Result<Vec<Entity>> {
        let mut executor = EntitiesQueryExecutor::new(query);
        let rows = executor.prepare_execute(&self)?;
        let start = Instant::now();
        let results = rows.mapped(row_to_entity).map(|e| e.expect("Failed to retrieve entity")).collect();
        debug!("Results retrieved in {:?}.", start.elapsed());
        Ok(results)
    }

    pub fn get_entities_really_intersecting(
        &self,
        candidate_ids: &[&str],
        x: f64,
        y: f64,
        fast: bool,
    ) -> Result<Vec<Entity>> {
        let mut candidate_params = vec![];
        for i in 0..candidate_ids.len() {
            candidate_params.push(format!(":candidate{}", i));
        }
        let mut query = format!("SELECT id, discriminator, AsBinary(geometry) as geometry, data, effective_width FROM entities WHERE id in ({})", candidate_params.join(","));
        if fast {
            query += " AND length(geometry) < 100000";
        }
        let fragment = format!(
            " AND St_Disjoint(geometry, GeomFromText('POINT({} {})', 4326)) = 0",
            x, y
        );
        query += &fragment;
        let mut params: Vec<(&str, &dyn ToSql)> = vec![];
        for (i, id) in candidate_ids.iter().enumerate() {
            params.push((&candidate_params[i], id));
        }
        debug!(
            "Executing inside of query: {:?} with parameters: {:?}",
            query, candidate_ids
        );
        let mut stmt = self.conn.prepare_cached(&query)?;
        let res = stmt
            .query_map_named(params.as_slice(), row_to_entity)
            .map_err(Error::from)?;
        Ok(res.map(|e| e.expect("Failed to retrieve entity")).collect())
    }

    fn insert_entity(
        &mut self,
        id: &str,
        discriminator: &str,
        geometry: &[u8],
        effective_width: &Option<f64>,
        data: &str,
        child_ids: &[String],
    ) -> Result<()> {
        let mut stmt = if self.geometry_is_valid(&geometry)? {
            self.conn.prepare_cached(INSERT_ENTITY_SQL)?
        } else {
            self.conn.prepare_cached(INSERT_ENTITY_SQL_BUFFERED)?
        };
        stmt.execute(params![id, discriminator, geometry, effective_width, data])?;
        let mut insert_child_id_stmt = self.conn.prepare_cached(INSERT_ENTITY_RELATIONSHIP_SQL)?;
        for child_id in child_ids {
            if let Err(e) = insert_child_id_stmt.execute(params![id, child_id, EntityRelationshipKind::OSMChild]) {
                match classify_db_error(&e, &child_id) {
                    ForeignKeyViolationClassification::Retryable => {
                        self.deferred_relationship_additions
                            .insert(id.to_string(), child_id.to_string());
                    }
                    ForeignKeyViolationClassification::Fatal => {
                        continue;
                    } // Now it only means that we tryed to insert a relationship for an entity which we definitely don't have in the database - relations are handled separately and anything else can only depend on a smaller object which was inserted before (because we do separate queries for node, way and relation changes and this can be called only from a change application)
                    ForeignKeyViolationClassification::NoViolation => {
                        return Err(Error::DbError(e));
                    }
                }
            }
        }
        Ok(())
    }

    fn remove_entity(&self, osm_id: &str) -> Result<()> {
        let mut stmt = self
            .conn
            .prepare_cached("delete from entities where id = ?")?;
        stmt.execute(&[&osm_id])?;
        Ok(())
    }

    fn save_updated_entity(&self, entity: &Entity) -> Result<()> {
        let mut stmt = if self.geometry_is_valid(&entity.geometry)? {
            self.conn.prepare_cached("update entities set discriminator = ?, geometry = GeomFromWKB(?, 4326), effective_width = ?, data = ? where id = ?;")?
        } else {
            self.conn.prepare_cached("update entities set discriminator = ?, geometry = Buffer(GeomFromWKB(?, 4326), 0), effective_width = ?, data = ? where id = ?;")?
        };
        stmt.execute(params![
            entity.discriminator,
            entity.geometry,
            entity.effective_width,
            entity.data,
            entity.id,
        ])?;
        Ok(())
    }

    pub fn apply_change(&mut self, change: &SemanticChange) -> Result<()> {
        use SemanticChange::*;
        match change {
            RedownloadDatabase => Err(Error::IllegalChangeType),
            Create {
                id,
                discriminator,
                geometry,
                effective_width,
                data,
                child_ids,
            } => self.insert_entity(
                &id,
                &discriminator,
                &base64::decode(&geometry).expect("Geometry should be base64 encoded"),
                &effective_width,
                &data,
                &child_ids,
            ),
            Remove { osm_id } => self.remove_entity(&osm_id),
            Update {
                osm_id,
                property_changes,
                data_changes,
                child_id_changes,
            } => {
                if let Some(mut entity) = self.get_entity(&osm_id)? {
                    entity.apply_property_changes(&property_changes);
                    entity.apply_data_changes(&data_changes);
                    self.save_updated_entity(&entity)?;
                    self.apply_child_id_changes(&entity.id, child_id_changes)
                } else {
                    warn!("Change application requested an update of non-existent entity with osm id {}.", osm_id);
                    Ok(())
                }
            }
        }
    }

    fn geometry_is_valid(&self, geometry: &[u8]) -> Result<bool> {
        let mut stmt = self
            .conn
            .prepare_cached("select isValid(geomFromWKB(?, 4326))")?;
        stmt.query_row(&[&geometry], |row| row.get(0))
            .map_err(Error::from)
    }

    pub fn begin(&self) -> Result<()> {
        let mut stmt = self.conn.prepare_cached("BEGIN")?;
        stmt.execute(NO_PARAMS)?;
        Ok(())
    }
    pub fn commit(&self) -> Result<()> {
        let mut stmt = self.conn.prepare_cached("COMMIT")?;
        stmt.execute(NO_PARAMS)?;
        Ok(())
    }

    fn apply_child_id_changes(&mut self, parent_id: &str, changes: &[ListChange]) -> Result<()> {
        for change in changes {
            match change {
                ListChange::Add { value } => {
                    if let Err(e) = self
                        .conn
                        .prepare_cached(INSERT_ENTITY_RELATIONSHIP_SQL)?
                        .execute(params![parent_id, value, EntityRelationshipKind::OSMChild])
                    {
                        match classify_db_error(&e, &value) {
                            ForeignKeyViolationClassification::Retryable => {
                                self.deferred_relationship_additions
                                    .insert(parent_id.to_string(), value.to_string());
                            }
                            ForeignKeyViolationClassification::Fatal => {
                                continue;
                            }
                            ForeignKeyViolationClassification::NoViolation => {
                                return Err(Error::DbError(e));
                            }
                        }
                    }
                }
                ListChange::Remove { value } => {
                    self.conn
                        .prepare_cached(
                            "DELETE FROM entity_relationships where parent_id = ? and child_id = ? AND kind = ?",
                        )?
                        .execute(params![parent_id, value, EntityRelationshipKind::OSMChild])?;
                }
            }
        }
        Ok(())
    }

    pub fn get_entity_child_ids(&self, parent_id: &str) -> Result<Vec<String>> {
        Ok(self
            .conn
            .prepare_cached("SELECT child_id from entity_relationships WHERE parent_id = ? AND kind = ?")?
            .query_and_then(params![parent_id, EntityRelationshipKind::OSMChild], |row| Ok(row.get_unwrap(0)))?
            .filter_map(Result::ok)
            .collect())
    }

    pub fn get_parent_count(&self, child_id: &str) -> Result<u32> {
        Ok(self
            .conn
            .prepare_cached("SELECT count(*) from entity_relationships WHERE child_id = ?")?
            .query_row(params![child_id, EntityRelationshipKind::OSMChild], |row| Ok(row.get_unwrap(0)))?)
    }
    pub fn get_child_count(&self, parent_id: &str) -> Result<u32> {
        Ok(self
            .conn
            .prepare_cached("SELECT count(*) from entity_relationships WHERE parent_id = ? AND kind = ?")?
            .query_row(params![parent_id, EntityRelationshipKind::OSMChild], |row| Ok(row.get_unwrap(0)))?)
    }

    fn insert_deferred_entity_relationship(&self, parent: &str, child: &str) -> Result<()> {
        let res = self
            .conn
            .prepare_cached(INSERT_ENTITY_RELATIONSHIP_SQL)?
            .execute(params![parent, child, EntityRelationshipKind::OSMChild]); // Whatever error there is fatal - the relationships should all be there and nothing else should be inserted to the relationships table at this point.
        if let Err(e) = res {
            match classify_db_error(&e, &child) {
                ForeignKeyViolationClassification::Retryable => {
                    warn!("Even after deferring the relationship insertions, the child entity with id {} failed to insert for parent entity {}.", child, parent);
                }
                _ => return Err(Error::DbError(e)),
            }
        }
        Ok(())
    }

    pub fn apply_deferred_relationship_additions(&mut self) -> Result<()> {
        for (parent, child) in self.deferred_relationship_additions.iter() {
            self.insert_deferred_entity_relationship(parent, child)?;
        }
        self.deferred_relationship_additions.clear();
        Ok(())
    }

    pub fn get_road_ids_with_name(&self, name:&str, ordered_by_distance_to: &str) -> Result<Vec<String>> {
        let mut stmt = self.conn.prepare_cached("select id from entities, (select geometry from entities where id = ? limit 1) as wanted where discriminator in ('Road', 'ServiceRoad', 'Track') and json_extract(data, '$.name') = ? order by distance(wanted.geometry, entities.geometry)")?;
let results = stmt.query_map(params![ordered_by_distance_to, name], |r| -> rusqlite::Result<String> {Ok(r.get_unwrap(0))})?.map(|e| e.expect("Should not happen")).collect();
Ok(results)
    }

    pub fn get_basic_contained_entities_info(&self, entity_id: &str) -> Result<Vec<BasicEntityInfo>> {
        let mut stmt = self.conn.prepare_cached("SELECT id, discriminator FROM entities, (SELECT geometry FROM entities WHERE id = ?) AS outer WHERE ND entities.rowid IN (SELECT rowid from SpatialIndex WHERE f_table_name = 'entities' AND search_frame = outer.geometry) AND contains(outer.geometry, entities.geometry)")?;
        let results = stmt.query_map(params![entity_id], |r| -> rusqlite::Result<BasicEntityInfo> {Ok(BasicEntityInfo{id:r.get_unwrap(0), discriminator:r.get_unwrap(1)})})?.map(|i| i.expect("Should not happen")).collect();
        Ok(results)
    }

    pub fn num_addressables_in(&self, entity_id: &str) -> Result<i64> {
        let mut stmt = self.conn.prepare_cached("SELECT count(*) FROM entities, (SELECT geometry FROM entities WHERE id = ?) AS outer WHERE entities.discriminator = 'Addressable' AND entities.rowid IN (SELECT rowid from SpatialIndex WHERE f_table_name = 'entities' AND search_frame = outer.geometry) AND contains(outer.geometry, entities.geometry)")?;
let num: i64 =      stmt.query_row(params![entity_id], |row| Ok(row.get_unwrap(0)))?;
Ok(num)
    }
    pub fn get_addressable_ids_in(&self, entity_id: &str) -> Result<Vec<String>> {
        let mut stmt = self.conn.prepare_cached("SELECT id FROM entities, (SELECT geometry FROM entities WHERE id = ?) AS outer WHERE discriminator = 'Addressable' AND entities.rowid IN (SELECT rowid from SpatialIndex WHERE f_table_name = 'entities' AND search_frame = outer.geometry) AND contains(outer.geometry, entities.geometry)")?;
        let results = stmt.query_map(params![entity_id], |r| -> rusqlite::Result<String> {Ok(r.get_unwrap(0))})?.map(|i| i.expect("Should not happen")).collect();
        Ok(results)
    }

}


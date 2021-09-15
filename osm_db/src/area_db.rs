use crate::entities_query_executor::EntitiesQueryExecutor;
use crate::entity::Entity;
use crate::entity_relationship::EntityRelationship;
use crate::entity_relationship_kind::EntityRelationshipKind;
use crate::semantic_change::{RelationshipChange, SemanticChange};
use crate::{entities_query::EntitiesQuery, entity_relationship::RootedEntityRelationship};
use crate::{Error, Result};
use log::{debug, error, info, trace, warn};
use osm_api::SmolStr;
use rusqlite::types::ToSql;
use rusqlite::{named_params, params, Connection, OpenFlags, Row};
use std::collections::HashMap;
use std::path::PathBuf;
use std::time::Instant;

const INIT_AREA_DB_SQL: &str = include_str!("init_area_db.sql");
const INSERT_ENTITY_SQL: &str = "insert into entities (id, discriminator, geometry, effective_width, data) values (?, ?, geomFromWKB(?, 4326), ?, ?)";
const INSERT_ENTITY_SQL_BUFFERED: &str = "insert into entities (id, discriminator, geometry, effective_width, data) values (?, ?, Buffer(geomFromWKB(?, 4326), 0), ?, ?)";
const INSERT_ENTITY_RELATIONSHIP_SQL: &str =
    "INSERT INTO entity_relationships (parent_id, child_id, kind) VALUES (?, ?, ?) ON CONFLICT DO NOTHING";

#[derive(PartialEq)]
enum ForeignKeyViolationClassification {
    Fatal,
    Retryable,
    NoViolation,
}

fn classify_db_error(err: &rusqlite::Error, child_id: &str) -> ForeignKeyViolationClassification {
    if let rusqlite::Error::SqliteFailure(_, Some(_msg)) = err {
        if child_id.starts_with('r') {
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
        id: SmolStr::new_inline(&row.get_unwrap::<_, String>(0)),
        geometry: row.get_unwrap(2),
        discriminator: SmolStr::new_inline(&row.get_unwrap::<_, String>(1)),
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
    deferred_relationship_additions: HashMap<String, RootedEntityRelationship>,
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
            let mut appdata_dir = dirs_next::data_local_dir().expect("No local app data dir");
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
                    entity.id.as_str(),
                    entity.discriminator.as_str(),
                    entity.geometry,
                    entity.effective_width,
                    entity.data,
                ]) {
                    Ok(_) => {
                        count += 1;
                        for related_id in related_ids {
                            if let Err(e) = insert_related_stmt.execute(params![
                                entity.id.as_str(),
                                related_id,
                                EntityRelationshipKind::OSMChild
                            ]) {
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
            self.insert_entity_relationship(&EntityRelationship::new(
                parent,
                child,
                EntityRelationshipKind::OSMChild,
            ))?;
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
        let rows = executor.prepare_execute(self)?;
        let start = Instant::now();
        let results = rows
            .mapped(row_to_entity)
            .map(|e| e.expect("Failed to retrieve entity"))
            .collect();
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
            .query_map(params.as_slice(), row_to_entity)
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
        entity_relationships: &[RootedEntityRelationship],
    ) -> Result<()> {
        let mut stmt = if self.geometry_is_valid(geometry)? {
            self.conn.prepare_cached(INSERT_ENTITY_SQL)?
        } else {
            self.conn.prepare_cached(INSERT_ENTITY_SQL_BUFFERED)?
        };
        stmt.execute(params![id, discriminator, geometry, effective_width, data])?;
        let mut insert_relationship_stmt =
            self.conn.prepare_cached(INSERT_ENTITY_RELATIONSHIP_SQL)?;
        for relationship in entity_relationships {
            if let Err(e) = insert_relationship_stmt.execute(params![
                id,
                relationship.child_id,
                relationship.kind
            ]) {
                match classify_db_error(&e, &relationship.child_id) {
                    ForeignKeyViolationClassification::Retryable => {
                        self.deferred_relationship_additions
                            .insert(id.to_string(), relationship.clone());
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
            entity.discriminator.as_str(),
            entity.geometry,
            entity.effective_width,
            entity.data,
            entity.id.as_str(),
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
                entity_relationships,
            } => self.insert_entity(
                id,
                discriminator,
                &base64::decode(&geometry).expect("Geometry should be base64 encoded"),
                effective_width,
                data,
                entity_relationships,
            ),
            Remove { osm_id } => self.remove_entity(osm_id),
            Update {
                osm_id,
                property_changes,
                data_changes,
                relationship_changes,
            } => {
                if let Some(mut entity) = self.get_entity(osm_id)? {
                    entity.apply_property_changes(property_changes);
                    entity.apply_data_changes(data_changes);
                    self.save_updated_entity(&entity)?;
                    self.apply_child_id_changes(&entity.id, relationship_changes)
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
        stmt.execute([])?;
        Ok(())
    }
    pub fn commit(&self) -> Result<()> {
        let mut stmt = self.conn.prepare_cached("COMMIT")?;
        stmt.execute([])?;
        Ok(())
    }

    fn apply_child_id_changes(
        &mut self,
        parent_id: &str,
        changes: &[RelationshipChange],
    ) -> Result<()> {
        for change in changes {
            match change {
                RelationshipChange::Add { value } => {
                    if let Err(e) = self
                        .conn
                        .prepare_cached(INSERT_ENTITY_RELATIONSHIP_SQL)?
                        .execute(params![parent_id, value.child_id, value.kind])
                    {
                        match classify_db_error(&e, &value.child_id) {
                            ForeignKeyViolationClassification::Retryable => {
                                self.deferred_relationship_additions
                                    .insert(parent_id.to_string(), value.clone());
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
                RelationshipChange::Remove { value } => {
                    self.conn
                        .prepare_cached(
                            "DELETE FROM entity_relationships where parent_id = ? and child_id = ? AND kind = ?",
                        )?
                        .execute(params![parent_id, value.child_id, value.kind])?;
                }
            }
        }
        Ok(())
    }

    pub fn get_entity_child_ids(&self, parent_id: &str) -> Result<Vec<String>> {
        Ok(self
            .conn
            .prepare_cached(
                "SELECT child_id from entity_relationships WHERE parent_id = ? AND kind = ?",
            )?
            .query_and_then(
                params![parent_id, EntityRelationshipKind::OSMChild],
                |row| Ok(row.get_unwrap(0)),
            )?
            .filter_map(Result::ok)
            .collect())
    }

    pub fn get_parent_count(&self, child_id: &str) -> Result<u32> {
        Ok(self
            .conn
            .prepare_cached(
                "SELECT count(*) from entity_relationships WHERE child_id = ? AND kind = ?",
            )?
            .query_row(params![child_id, EntityRelationshipKind::OSMChild], |row| {
                Ok(row.get_unwrap(0))
            })?)
    }
    pub fn get_child_count(&self, parent_id: &str) -> Result<u32> {
        Ok(self
            .conn
            .prepare_cached(
                "SELECT count(*) from entity_relationships WHERE parent_id = ? AND kind = ?",
            )?
            .query_row(
                params![parent_id, EntityRelationshipKind::OSMChild],
                |row| Ok(row.get_unwrap(0)),
            )?)
    }

    pub(crate) fn insert_entity_relationship(
        &self,
        relationship: &EntityRelationship,
    ) -> Result<()> {
        let res = self
            .conn
            .prepare_cached(INSERT_ENTITY_RELATIONSHIP_SQL)?
            .execute(params![
                relationship.parent_id.as_str(),
                relationship.child_id.as_str(),
                relationship.kind
            ]); // Whatever error there is fatal - the relationships should all be there and nothing else should be inserted to the relationships table at this point.
        if let Err(e) = res {
            match classify_db_error(&e, &relationship.child_id) {
                ForeignKeyViolationClassification::Retryable => {
                    warn!("Failed to insert entity relationship {:?}.", relationship);
                }
                _ => return Err(Error::DbError(e)),
            }
        }
        Ok(())
    }

    pub fn apply_deferred_relationship_additions(&mut self) -> Result<()> {
        for (parent, child) in self.deferred_relationship_additions.iter() {
            self.insert_entity_relationship(&EntityRelationship::new(
                parent,
                &child.child_id,
                child.kind,
            ))?;
        }
        self.deferred_relationship_additions.clear();
        Ok(())
    }

    pub fn get_road_ids_with_name(
        &self,
        name: &str,
        ordered_by_distance_to: &str,
    ) -> Result<Vec<String>> {
        let mut stmt = self.conn.prepare_cached("select id from entities, (select geometry from entities where id = ? limit 1) as wanted where discriminator in ('Road', 'ServiceRoad', 'Track') and lower(json_extract(data, '$.name')) = lower(?) order by distance(wanted.geometry, entities.geometry)")?;
        let results = stmt
            .query_map(
                params![ordered_by_distance_to, name],
                |r| -> rusqlite::Result<String> { Ok(r.get_unwrap(0)) },
            )?
            .map(|e| e.expect("Should not happen"))
            .collect();
        Ok(results)
    }

    pub fn get_contained_entity_ids(&self, entity_id: &str) -> Result<Vec<String>> {
        let mut stmt = self.conn.prepare_cached("SELECT id FROM entities, (SELECT geometry FROM entities WHERE id = ?) AS outer WHERE entities.id not like 'r%' AND entities.rowid IN (SELECT rowid from SpatialIndex WHERE f_table_name = 'entities' AND search_frame = outer.geometry) AND contains(outer.geometry, entities.geometry)")?;
        let results = stmt
            .query_map(params![entity_id], |r| -> rusqlite::Result<String> {
                Ok(r.get_unwrap(0))
            })?
            .map(|i| i.expect("Should not happen"))
            .collect();
        Ok(results)
    }

    pub fn num_addressables_in(&self, entity_id: &str, only_with_streets: bool) -> Result<i64> {
        let query = if only_with_streets {
            "SELECT count(*) FROM entities, (SELECT geometry FROM entities WHERE id = ?) AS outer WHERE entities.discriminator = 'Addressable' AND entities.rowid IN (SELECT rowid from SpatialIndex WHERE f_table_name = 'entities' AND search_frame = outer.geometry) AND contains(outer.geometry, entities.geometry) AND json_extract(entities.data, '$.address.street') IS NOT NULL"
        } else {
            "SELECT count(*) FROM entities, (SELECT geometry FROM entities WHERE id = ?) AS outer WHERE entities.discriminator = 'Addressable' AND entities.rowid IN (SELECT rowid from SpatialIndex WHERE f_table_name = 'entities' AND search_frame = outer.geometry) AND contains(outer.geometry, entities.geometry)"
        };
        let mut stmt = self.conn.prepare_cached(query)?;
        let num: i64 = stmt.query_row(params![entity_id], |row| Ok(row.get_unwrap(0)))?;
        Ok(num)
    }
    pub fn get_addressable_ids_in(
        &self,
        entity_id: &str,
        only_with_streets: bool,
    ) -> Result<Vec<String>> {
        let query = if only_with_streets {
            "SELECT id FROM entities, (SELECT geometry FROM entities WHERE id = ?) AS outer WHERE discriminator = 'Addressable' AND entities.rowid IN (SELECT rowid from SpatialIndex WHERE f_table_name = 'entities' AND search_frame = outer.geometry) AND contains(outer.geometry, entities.geometry) AND json_extract(entities.data, '$.address.street') IS NOT NULL"
        } else {
            "SELECT id FROM entities, (SELECT geometry FROM entities WHERE id = ?) AS outer WHERE discriminator = 'Addressable' AND entities.rowid IN (SELECT rowid from SpatialIndex WHERE f_table_name = 'entities' AND search_frame = outer.geometry) AND contains(outer.geometry, entities.geometry)"
        };
        let mut stmt = self.conn.prepare_cached(query)?;
        let results = stmt
            .query_map(params![entity_id], |r| -> rusqlite::Result<String> {
                Ok(r.get_unwrap(0))
            })?
            .map(|i| i.expect("Should not happen"))
            .collect();
        Ok(results)
    }

    pub fn get_relationships_related_to(&self, entity_id: &str) -> Result<Vec<EntityRelationship>> {
        let mut stmt = self.conn.prepare_cached("SELECT parent_id, child_id, kind FROM entity_relationships WHERE parent_id = :entity_id OR child_id = :entity_id")?;
        let results = stmt
            .query_map(
                named_params! {":entity_id": entity_id},
                |row| -> rusqlite::Result<EntityRelationship> {
                    Ok(EntityRelationship::new(
                        &row.get_unwrap::<_, String>(0),
                        &row.get_unwrap::<_, String>(1),
                        row.get_unwrap(2),
                    ))
                },
            )?
            .map(|e| e.expect("Should not happen"))
            .collect();
        Ok(results)
    }

    fn num_rows_in_table(&self, table: &str) -> Result<usize> {
        let mut stmt = self.conn.prepare_cached(&format!("SELECT count(*) from {}", table))?;
        Ok(stmt.query_row([], |row| Ok(row.get_unwrap(0)))?)
    }

    pub fn num_entities(&self) -> Result<usize> {
        self.num_rows_in_table("entities")
    }
    pub fn num_entity_relationships(&self) -> Result<usize> {
        self.num_rows_in_table("entity_relationships")
    }
    
    pub fn get_entity_counts_by_discriminator(&self) -> Result<HashMap<String, usize>> {
        let mut stmt = self.conn.prepare_cached("SELECT discriminator, count(*) FROM entities GROUP BY discriminator")?;
        let results = stmt.query_map([], |row| Ok((row.get_unwrap(0), row.get_unwrap(1))))?.map(|e| e.expect("Should not happen")).collect();
        Ok(results)
    }

    pub fn get_entity_relationship_counts_by_kind(&self) -> Result<HashMap<String, usize>> {
        let mut stmt = self.conn.prepare_cached("SELECT kind, count(*) FROM entity_relationships GROUP BY discriminator")?;
        let results = stmt.query_map([], |row| Ok((format!("{:?}", row.get_unwrap::<_, EntityRelationshipKind>(0)), row.get_unwrap(1))))?.map(|e| e.expect("Should not happen")).collect();
        Ok(results)
    }
    }

use crate::entities_query::EntitiesQuery;
use crate::entity::Entity;
use crate::semantic_change::{ListChange, SemanticChange};
use crate::{Error, Result};
use rusqlite::types::ToSql;
use rusqlite::{params, Connection, OpenFlags, Row, Transaction, NO_PARAMS};
use std::path::PathBuf;
use std::time::Instant;

const INIT_AREA_DB_SQL: &str = include_str!("init_area_db.sql");
const INSERT_ENTITY_SQL: &str = "insert into entities (id, discriminator, geometry, effective_width, data) values (?, ?, geomFromWKB(?, 4326), ?, ?)";
const INSERT_ENTITY_SQL_BUFFERED: &str = "insert into entities (id, discriminator, geometry, effective_width, data) values (?, ?, Buffer(geomFromWKB(?, 4326), 0), ?, ?)";
const INSERT_ENTITY_RELATIONSHIP_SQL: &str =
    "INSERT INTO entity_relationships (parent_id, child_id) VALUES (?, ?)";

fn is_foreign_key_violation(err: &rusqlite::Error, parent_id: &str, child_id: &str) -> bool {
    if let rusqlite::Error::SqliteFailure(_, Some(_msg)) = err {
        if child_id.chars().nth(0).unwrap() == 'r' {
            warn!("Entity {} has as a child the relation {} but we did not insert it into the db yet.", parent_id, child_id);
        }
        return true; // We just tried to insert a relationship for an entity which we don't know, but that's fine.
    } else {
        return false;
    }
}

fn row_to_entity(row: &Row) -> core::result::Result<Entity, rusqlite::Error> {
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

fn geometry_is_valid_transacted(geometry: &[u8], tx: &Transaction) -> Result<bool> {
    let mut stmt = tx.prepare_cached("select isValid(geomFromWKB(?, 4326))")?;
    stmt.query_row(&[&geometry], |row| row.get(0))
        .map_err(Error::from)
}

pub struct AreaDatabase {
    conn: Connection,
}

impl AreaDatabase {
    fn common_construct(conn: Connection) -> Result<Self> {
        conn.execute("PRAGMA foreign_keys=on", params![])?;
        Ok(Self { conn })
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
        let insert_tx = self.conn.transaction()?;
        for (entity, related_ids) in entities {
            let mut insert_related_stmt =
                insert_tx.prepare_cached(INSERT_ENTITY_RELATIONSHIP_SQL)?;
            if entity.geometry.len() < 1_000_000 {
                let mut insert_stmt = if geometry_is_valid_transacted(&entity.geometry, &insert_tx)?
                {
                    insert_tx.prepare(INSERT_ENTITY_SQL)?
                } else {
                    insert_tx.prepare(INSERT_ENTITY_SQL_BUFFERED)?
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
                                insert_related_stmt.execute(params![entity.id, related_id])
                            {
                                if is_foreign_key_violation(&e, &entity.id, &related_id) {
                                    continue; // We just tried to insert a relationship for an entity which we don't know, but that's fine.
                                } else {
                                    return Err(Error::DbError(e));
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
        insert_tx.commit()?;
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
        debug!("About to execute query {}", query.to_query_sql());
        let mut stmt = self.conn.prepare_cached(&query.to_query_sql())?;
        let orig_params = query.to_query_params();
        let mut params = vec![];
        for (name, value) in &orig_params {
            params.push((name.as_str(), *value));
        }
        let now = Instant::now();
        let res = stmt.query_map_named(params.as_slice(), row_to_entity)?;
        debug!("Query_map_named took {:?}", now.elapsed());
        let results = res.map(|e| e.expect("Failed to retrieve entity")).collect();
        debug!("Query results retrieval took {:?}", now.elapsed());
        Ok(results)
    }

    pub fn get_entities_really_intersecting(
        &self,
        candidate_ids: &[i32],
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
            " AND contains(geometry, GeomFromText('POINT({} {})', 4326))",
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
        &self,
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
            if let Err(e) = insert_child_id_stmt.execute(params![id, child_id]) {
                if is_foreign_key_violation(&e, &id, &child_id) {
                    continue;
                } else {
                    return Err(Error::DbError(e));
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

    pub fn apply_change(&self, change: &SemanticChange) -> Result<()> {
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

    fn apply_child_id_changes(&self, parent_id: &str, changes: &[ListChange]) -> Result<()> {
        for change in changes {
            match change {
                ListChange::Add { value } => {
                    self.conn
                        .prepare_cached(INSERT_ENTITY_RELATIONSHIP_SQL)?
                        .execute(params![parent_id, value])?;
                }
                ListChange::Remove { value } => {
                    self.conn
                        .prepare_cached(
                            "DELETE FROM entity_relationships where parent_id = ? and child_id = ?",
                        )?
                        .execute(params![parent_id, value])?;
                }
            }
        }
        Ok(())
    }

    pub fn get_entity_child_ids(&self, parent_id: &str) -> Result<Vec<String>> {
        Ok(self
            .conn
            .prepare_cached("SELECT child_id from entity_relationships WHERE parent_id = ?")?
            .query_and_then(params![parent_id], |row| Ok(row.get_unwrap(0)))?
            .filter_map(Result::ok)
            .collect())
    }
}

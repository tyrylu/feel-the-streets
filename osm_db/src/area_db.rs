use crate::entities_query::EntitiesQuery;
use crate::entity::{Entity, NotStoredEntity};
use crate::semantic_change::SemanticChange;
use rusqlite::{Connection, Error, OpenFlags, Row, Transaction};
use rusqlite::types::ToSql;
use std::path::PathBuf;
use std::time::Instant;

type DbResult<T> = Result<T, rusqlite::Error>;

const INIT_AREA_DB_SQL: &str = include_str!("init_area_db.sql");
const INSERT_ENTITY_SQL: &str = "insert into entities (discriminator, geometry, effective_width, data) values (?, geomFromText(?, 4326), ?, ?)";
const INSERT_ENTITY_SQL_BUFFERED: &str = "insert into entities (discriminator, geometry, effective_width, data) values (?, Buffer(geomFromText(?, 4326), 0), ?, ?)";

fn row_to_entity(row: &Row) -> Entity {
    Entity {
        id: row.get(0),
        geometry: row.get(2),
        discriminator: row.get(1),
        data: row.get(3),
        effective_width: row.get(4),
        parsed_data: None,
    }
}

fn init_extensions(conn: &Connection) -> DbResult<()> {
    conn.load_extension_enable()?;
    conn.load_extension("mod_spatialite", None)?;
    Ok(())
}

fn geometry_is_valid_transacted(geometry: &str, tx: &Transaction) -> DbResult<bool> {
    let mut stmt = tx.prepare_cached("select isValid(geomFromText(?, 4326))")?;
    stmt.query_row(&[&geometry], |row| row.get(0))
}

pub struct AreaDatabase {
    conn: Connection,
}

impl AreaDatabase {
    fn common_construct(conn: Connection) -> DbResult<Self> {
        Ok(Self { conn })
    }

    pub fn path_for(area: &str, server_side: bool) -> PathBuf {
        let mut root = if server_side {
            PathBuf::from(".")
        } else {
            let mut appdata_dir = dirs::data_local_dir().expect("No local app data dir");
            appdata_dir.push("fts/areas");
            appdata_dir
        };
        root.push(format!("{}.db", area));
        root
    }

    pub fn create(area: &str) -> DbResult<Self> {
        let conn = Connection::open(&AreaDatabase::path_for(&area, true))?;
        init_extensions(&conn)?;
        conn.execute_batch(INIT_AREA_DB_SQL)?;
        AreaDatabase::common_construct(conn)
    }
    pub fn open_existing(area: &str, server_side: bool) -> DbResult<Self> {
        let conn = Connection::open_with_flags(
            &AreaDatabase::path_for(&area, server_side),
            OpenFlags::SQLITE_OPEN_READ_WRITE,
        )?;
        init_extensions(&conn)?;
        AreaDatabase::common_construct(conn)
    }

    pub fn insert_entities<T>(&mut self, entities: T) -> DbResult<()>
    where
        T: Iterator<Item = NotStoredEntity>,
    {
        let mut count = 0;
        let insert_tx = self.conn.transaction()?;
        for entity in entities {
            if entity.geometry.len() < 1_000_000 {
                let mut insert_stmt = if geometry_is_valid_transacted(&entity.geometry, &insert_tx)?
                {
                    insert_tx.prepare(INSERT_ENTITY_SQL)?
                } else {
                    insert_tx.prepare(INSERT_ENTITY_SQL_BUFFERED)?
                };
                trace!("Inserting {:?}", entity);
                match insert_stmt.execute(&[
                    &entity.discriminator,
                    &entity.geometry,
                    &entity.effective_width,
                    &entity.data,
                ]) {
                    Ok(_) => count += 1,
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

    pub fn has_entity(&self, osm_id: &str) -> DbResult<bool> {
        let mut stmt = self
            .conn
            .prepare_cached("select id from entities where json_extract(data, '$.osm_id') = ?")?;
        stmt.exists(&[&osm_id])
    }

    pub fn get_entity(&self, osm_id: &str) -> DbResult<Option<Entity>> {
        let mut stmt = self.conn.prepare_cached("select id, discriminator, AsText(geometry) as geometry, data, effective_width from entities where json_extract(data, '$.osm_id') = ?")?;
        match stmt.query_row(&[&osm_id], row_to_entity) {
            Ok(e) => Ok(Some(e)),
            Err(e) => match e {
                Error::QueryReturnedNoRows => Ok(None),
                _ => Err(e),
            },
        }
    }
    pub fn get_entities(&self, query: &EntitiesQuery) -> DbResult<Vec<Entity>> {
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
    ) -> DbResult<Vec<Entity>> {
        let mut candidate_params = vec![];
        for i in 0..candidate_ids.len() {
            candidate_params.push(format!(":candidate{}", i));
        }
        let mut query = format!("SELECT id, discriminator, AsText(geometry) as geometry, data, effective_width FROM entities WHERE id in ({})", candidate_params.join(","));
        if fast {
            query += " AND length(geometry) < 100000";
        }
        let fragment = format!(" AND contains(geometry, GeomFromText('POINT({} {})', 4326))", x, y);
        query += &fragment;
        let mut params: Vec<(&str, &dyn ToSql)> = vec![];
        for (i, id) in candidate_ids.iter().enumerate() {
            params.push((&candidate_params[i], id));
        }
        debug!("Executing inside of query: {:?} with parameters: {:?}", query, candidate_ids);
        let mut stmt = self.conn.prepare_cached(&query)?;
        let res = stmt.query_map_named(params.as_slice(), row_to_entity)?;
        Ok(res.map(|e| e.expect("Failed to retrieve entity")).collect())
    }

    fn insert_entity(
        &self,
        discriminator: &str,
        geometry: &str,
        effective_width: &Option<f64>,
        data: &str,
    ) -> DbResult<()> {
        let mut stmt = if self.geometry_is_valid(&geometry)? {
            self.conn.prepare_cached(INSERT_ENTITY_SQL)?
        } else {
            self.conn.prepare_cached(INSERT_ENTITY_SQL_BUFFERED)?
        };
        stmt.execute(&[&discriminator, &geometry, effective_width, &data])?;
        Ok(())
    }

    fn remove_entity(&self, osm_id: &str) -> DbResult<()> {
        let mut stmt = self
            .conn
            .prepare_cached("delete from entities where json_extract(data, '$.osm_id') = ?")?;
        stmt.execute(&[&osm_id])?;
        Ok(())
    }

    fn save_updated_entity(&self, entity: &Entity) -> DbResult<()> {
        let mut stmt = if self.geometry_is_valid(&entity.geometry)? {
            self.conn.prepare_cached("update entities set discriminator = ?, geometry = GeomFromText(?, 4326), effective_width = ?, data = ? where id = ?;")?
        } else {
            self.conn.prepare_cached("update entities set discriminator = ?, geometry = Buffer(GeomFromText(?, 4326), 0), effective_width = ?, data = ? where id = ?;")?
        };
        stmt.execute(&[
            &entity.discriminator,
            &entity.geometry,
            &entity.effective_width,
            &entity.data,
            &entity.id,
        ])?;
        Ok(())
    }

    pub fn apply_change(&self, change: &SemanticChange) -> DbResult<()> {
        use SemanticChange::*;
        match change {
            Create {
                discriminator,
                geometry,
                effective_width,
                data,
            } => self.insert_entity(&discriminator, &geometry, &effective_width, &data),
            Remove { osm_id } => self.remove_entity(&osm_id),
            Update {
                osm_id,
                property_changes,
                data_changes,
            } => {
                if let Some(mut entity) = self.get_entity(&osm_id)? {
                    entity.apply_property_changes(&property_changes);
                    entity.apply_data_changes(&data_changes);
                    self.save_updated_entity(&entity)
                } else {
                    warn!("Change application requested an update of non-existent entity with osm id {}.", osm_id);
                    Ok(())
                }
            }
        }
    }

    fn geometry_is_valid(&self, geometry: &str) -> DbResult<bool> {
        let mut stmt = self
            .conn
            .prepare_cached("select isValid(geomFromText(?, 4326))")?;
        stmt.query_row(&[&geometry], |row| row.get(0))
    }

    pub fn begin(&self) -> DbResult<()> {
        let mut stmt = self.conn.prepare_cached("BEGIN")?;
        stmt.execute(&[])?;
        Ok(())
    }
pub fn commit(&self) -> DbResult<()> {
        let mut stmt = self.conn.prepare_cached("COMMIT")?;
        stmt.execute(&[])?;
        Ok(())
    }
}

use crate::entity::{Entity, NotStoredEntity};
use crate::semantic_change::SemanticChange;
use rusqlite::{Connection, Error, OpenFlags};

type DbResult<T> = Result<T, rusqlite::Error>;

const INIT_AREA_DB_SQL: &str = include_str!("init_area_db.sql");
const INSERT_ENTITY_SQL: &str = "insert into entities (discriminator, geometry, effective_width, data) values (?, geomFromText(?, 4326), ?, ?)";

fn init_extensions(conn: &Connection) -> DbResult<()> {
    conn.load_extension_enable()?;
    conn.load_extension("mod_spatialite", None)?;
    Ok(())
}

pub struct AreaDatabase {
    conn: Connection,
}

impl AreaDatabase {
    fn common_construct(conn: Connection) -> DbResult<Self> {
        Ok(Self { conn })
    }

    pub fn path_for(area: &str) -> String {
        format!("{}.db", area)
    }

    pub fn create(area: &str) -> DbResult<Self> {
        let conn = Connection::open(&AreaDatabase::path_for(&area))?;
        init_extensions(&conn)?;
        conn.execute_batch(INIT_AREA_DB_SQL)?;
        AreaDatabase::common_construct(conn)
    }
    pub fn open_existing(area: &str) -> DbResult<Self> {
        let conn = Connection::open_with_flags(
            &AreaDatabase::path_for(&area),
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
        {
            let mut insert_stmt = insert_tx.prepare(INSERT_ENTITY_SQL)?;
            for entity in entities {
                if entity.geometry.len() < 1000000 {
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
        let mut stmt = self.conn.prepare_cached("select id, AsText(geometry) as geometry, discriminator, data, effective_width from entities where json_extract(data, '$.osm_id') = ?")?;
        match stmt.query_row(&[&osm_id], |row| Entity {
            id: row.get(0),
            geometry: row.get(1),
            discriminator: row.get(2),
            data: row.get(3),
            effective_width: row.get(4),
        }) {
            Ok(e) => Ok(Some(e)),
            Err(e) => match e {
                Error::QueryReturnedNoRows => Ok(None),
                _ => Err(e),
            },
        }
    }

    fn insert_entity(
        &self,
        discriminator: &str,
        geometry: &str,
        effective_width: &Option<f64>,
        data: &str,
    ) -> DbResult<()> {
        let mut stmt = self.conn.prepare_cached(INSERT_ENTITY_SQL)?;
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
        let mut stmt = self.conn.prepare_cached("update entities set discriminator = ?, geometry = GeomFromText(?, 4326), effective_width = ?, data = ? where id = ?;")?;
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
}

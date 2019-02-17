use crate::entity::{Entity, NotStoredEntity};
use rusqlite::{Connection, Error, OpenFlags};

type DbResult<T> = Result<T, rusqlite::Error>;

const INIT_AREA_DB_SQL: &str = include_str!("init_area_db.sql");

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
        let insert_tx = self.conn.transaction()?;
        {
            let mut insert_stmt = insert_tx.prepare("insert into entities (discriminator, geometry, effective_width, data) values (?, geomFromText(?, 4326), ?, ?)")?;
            for entity in entities {
                if entity.geometry.len() < 1000000 {
                    trace!(
                        "Inserting {} with geometry {}, effective width {:?} and data {}",
                        entity.discriminator,
                        entity.geometry,
                        entity.effective_width,
                        entity.data
                    );
                    insert_stmt.execute(&[
                        &entity.discriminator,
                        &entity.geometry,
                        &entity.effective_width,
                        &entity.data,
                    ])?;
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
        Ok(())
    }

    pub fn has_entity(&self, osm_id: &str) -> DbResult<bool> {
        let mut stmt = self
            .conn
            .prepare_cached("select id from entities where json_extract(data, '$.osm_id') = ?")?;
        stmt.exists(&[&osm_id])
    }

    pub fn get_entity(&self, osm_id: &str) -> DbResult<Option<Entity>> {
        let mut stmt = self.conn.prepare_cached("select id, GeomToText(geometry) as geometry, discriminator, data, effective_width from entities where json_extract(data, '$.osm_id') = ?")?;
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
}

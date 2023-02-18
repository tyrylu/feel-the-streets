use crate::Result;
use chrono::{Utc, DateTime};
use osm_db::AreaDatabase;
use rusqlite::{Connection,Row};
use rusqlite::types::{FromSql, ToSql};
use serde::Serialize;
use std::fs;

const ALL_AREA_COLUMNS: &str = "id, osm_id, name, state, created_at, updated_at, newest_osm_object_timestamp, db_size, parent_osm_ids, last_update_remark, geometry";
const SELECT_SOME_AREAS: &str = "SELECT id, osm_id, name, state, created_at, updated_at, newest_osm_object_timestamp, db_size, parent_osm_ids, last_update_remark, geometry";

fn row_to_area(row: &'_ Row<'_>) -> rusqlite::Result<Area> {
Ok(Area { id: row.get_unwrap(0), osm_id: row.get_unwrap(1), name: row.get_unwrap(2), state: row.get_unwrap(3), created_at: row.get_unwrap(4), updated_at: row.get_unwrap(5), newest_osm_object_timestamp: row.get_unwrap(6), db_size: row.get_unwrap(7)
    , parent_osm_ids: row.get_unwrap(8), last_update_remark: row.get_unwrap(9), geometry: row.get_unwrap(10) })
}

#[derive(PartialEq, Eq, Serialize, Debug)]
pub enum AreaState {
    Creating,
    ApplyingChanges,
    GettingChanges,
    Updated,
    Frozen,
}

impl FromSql for AreaState {
    fn column_result(value: rusqlite::types::ValueRef<'_>) -> rusqlite::types::FromSqlResult<Self> {
        match value.as_str()? {
            "updated" => Ok(AreaState::Updated),
            "creating" => Ok(AreaState::Creating),
            "applying_changes" => Ok(AreaState::ApplyingChanges),
            "getting_changes" => Ok(AreaState::GettingChanges),
            "frozen" => Ok(AreaState::Frozen),
            _ => Err(rusqlite::types::FromSqlError::Other("Invalid value for AreaState".into()))
        }
    }
}

impl ToSql for AreaState {
    fn to_sql(&self) -> rusqlite::Result<rusqlite::types::ToSqlOutput<'_>> {
        match self {
            AreaState::Creating => Ok("creating".to_string().into()),
            AreaState::ApplyingChanges => Ok("applying_changes".to_string().into()),
            AreaState::GettingChanges => Ok("getting_changes".to_string().into()),
            AreaState::Updated => Ok("updated".to_string().into()),
            AreaState::Frozen => Ok("frozen".to_string().into()),
        }
    }
}

#[derive(Serialize)]
pub struct Area {
    pub id: i32,
    pub osm_id: i64,
    pub name: String,
    pub state: AreaState,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub newest_osm_object_timestamp: Option<String>,
    pub db_size: i64,
    pub parent_osm_ids: Option<String>,
    pub last_update_remark: Option<String>,
    pub geometry: Option<Vec<u8>>,
}

impl Area {
    pub fn all(conn: &mut Connection) -> Result<Vec<Area>> {
        let mut stmt = conn.prepare_cached(&format!("{SELECT_SOME_AREAS} ORDER BY name"))?;
        let areas = stmt.query_map((), row_to_area)?.map(|a| a.expect("Could not get area")).collect();
        Ok(areas)
    }

    pub fn find_by_id(id: i32, conn: &mut Connection) -> Result<Area> {
        let mut stmt = conn.prepare_cached(&format!("{SELECT_SOME_AREAS} WHERE id = ?"))?;
        Ok(stmt.query_row([id], row_to_area)?)
    }

    pub fn find_by_osm_id(id: i64, conn: &mut Connection) -> Result<Area> {
        let mut stmt = conn.prepare_cached(&format!("{SELECT_SOME_AREAS} WHERE osm_id = ?"))?;
        Ok(stmt.query_row([id], row_to_area)?)
    }
    
    pub fn create(osm_id: i64, name: &str, conn: &mut Connection) -> Result<Area> {
        let now = Utc::now();
        let mut stmt = conn.prepare_cached(&format!("INSERT INTO areas (osm_id, name, state, created_at, updated_at) VALUES (?, ?, ?, ?, ?) RETURNING {ALL_AREA_COLUMNS}"))?;
        Ok(stmt.query_row((osm_id, name, AreaState::Creating, now, now), row_to_area)?)
    }
    
    pub fn all_updated(conn: &mut Connection) -> Result<Vec<Area>> {
        let mut stmt = conn.prepare_cached(&format!("{SELECT_SOME_AREAS} WHERE state = ?"))?;
        let areas = stmt.query_map([AreaState::Updated], row_to_area)?.map(|a| a.expect("Could not get area")).collect();
        Ok(areas)
            }

    pub fn save(&mut self, conn: &mut Connection) -> Result<()> {
    self.updated_at = Utc::now();
        let mut stmt = conn.prepare_cached("UPDATE areas SET (osm_id = ?, state = ?, name = ?, created_at = ?, updated_at = ?, newest_osm_object_timestamp = ?, db_size = ?, parent_osm_ids = ?, last_update_remark = ?, geometry = ?) where id = ?")?;
        stmt.execute((&self.osm_id, &self.state, &self.name, self.created_at, self.updated_at, &self.newest_osm_object_timestamp, self.db_size, &self.parent_osm_ids, &self.last_update_remark, &self.geometry, self.id))?;
        Ok(())
    }
}

pub fn finalize_area_creation(
    osm_id: i64,
    parent_ids_str: String,
    conn: &mut Connection,
) -> Result<usize> {
    let size = fs::metadata(AreaDatabase::path_for(osm_id, true))?.len();
    let mut stmt = conn.prepare_cached("UPDATE areas SET (state = ?, parent_osm_ids = ?, db_size = ?, updated_at = ?) WHERE osm_id = ?")?;
    Ok(stmt.execute((AreaState::Updated, parent_ids_str, size as i64, Utc::now(), osm_id))?)
}

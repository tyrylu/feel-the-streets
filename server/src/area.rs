use crate::schema::areas;
use crate::Result;
use chrono::{Utc, NaiveDateTime};
use diesel::dsl::now;
use diesel::prelude::*;
use diesel::SqliteConnection;
use diesel_derive_enum::DbEnum;
use osm_db::AreaDatabase;
use serde::Serialize;
use std::fs;

#[derive(PartialEq, Eq, Serialize, DbEnum, Debug)]
pub enum AreaState {
    Creating,
    ApplyingChanges,
    GettingChanges,
    Updated,
    Frozen,
}

#[derive(Serialize, Queryable, Identifiable, AsChangeset)]
pub struct Area {
    pub id: i32,
    pub osm_id: i64,
    pub name: String,
    pub state: AreaState,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub newest_osm_object_timestamp: Option<String>,
    pub db_size: i64,
    pub parent_osm_ids: Option<String>,
    pub last_update_remark: Option<String>,
    pub geometry: Option<Vec<u8>>,
}

impl Area {
    pub fn all(conn: &mut SqliteConnection) -> QueryResult<Vec<Area>> {
        areas::dsl::areas.order(areas::name.asc()).load(conn)
    }

    pub fn find_by_id(id: i32, conn: &mut SqliteConnection) -> QueryResult<Area> {
        areas::table.find(id).get_result(conn)
    }

    pub fn find_by_osm_id(id: i64, conn: &mut SqliteConnection) -> QueryResult<Area> {
        areas::table.filter(areas::osm_id.eq(id)).get_result(conn)
    }

    pub fn create(osm_id: i64, name: &str, conn: &mut SqliteConnection) -> QueryResult<Area> {
        // Sqlite3 does not support the returning clause...
        diesel::insert_into(areas::table)
            .values((
                areas::osm_id.eq(osm_id),
                areas::name.eq(name),
                areas::state.eq(AreaState::Creating),
                areas::created_at.eq(diesel::dsl::now),
                areas::updated_at.eq(diesel::dsl::now),
            ))
            .execute(conn)?;
        areas::dsl::areas
            .order(areas::id.desc())
            .limit(1)
            .get_result(conn)
    }
    
    pub fn all_updated(conn: &mut SqliteConnection) -> QueryResult<Vec<Area>> {
        areas::dsl::areas
            .filter(areas::state.eq(AreaState::Updated))
            .load(conn)
    }

    pub fn save(&mut self, conn: &mut SqliteConnection) -> QueryResult<Area> {
    self.updated_at = Utc::now().naive_local();
        self.save_changes(conn)    
    }
}

pub fn finalize_area_creation(
    osm_id: i64,
    parent_ids_str: String,
    conn: &mut SqliteConnection,
) -> Result<usize> {
    let size = fs::metadata(AreaDatabase::path_for(osm_id, true))?.len();
    let query = diesel::update(areas::table)
        .filter(areas::osm_id.eq(osm_id))
        .set((
            areas::state.eq(AreaState::Updated),
            areas::updated_at.eq(now),
            areas::db_size.eq(size as i64),
            areas::newest_osm_object_timestamp.eq(Option::<String>::None),
            areas::parent_osm_ids.eq(parent_ids_str),
        ));
    Ok(query.execute(conn)?)
}

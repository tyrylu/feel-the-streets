use crate::schema::areas;
use chrono::NaiveDateTime;
use diesel::dsl::now;
use diesel::prelude::*;
use diesel::SqliteConnection;
use diesel_derive_enum::DbEnum;
use serde::Serialize;
use log::debug;

#[derive(PartialEq, Serialize, DbEnum, Debug)]
pub enum AreaState {
    Creating,
    ApplyingChanges,
    GettingChanges,
    Updated,
}

#[derive(Serialize, Queryable, AsChangeset)]
pub struct Area {
    pub id: i32,
    pub name: String,
    pub state: AreaState,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub newest_osm_object_timestamp: Option<String>,
}

impl Area {
    pub fn all(conn: &SqliteConnection) -> QueryResult<Vec<Area>> {
        areas::dsl::areas.order(areas::name.asc()).load(conn)
    }

    pub fn find_by_id(id: i32, conn: &SqliteConnection) -> QueryResult<Area> {
        areas::table.find(id).get_result(conn)
    }

    pub fn find_by_name(name: &str, conn: &SqliteConnection) -> QueryResult<Area> {
        areas::table.filter(areas::name.eq(name)).get_result(conn)
    }

    pub fn create(name: &str, conn: &SqliteConnection) -> QueryResult<Area> {
        // Sqlite3 does not support the returning clause...
        diesel::insert_into(areas::table)
            .values((
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
    pub fn all_updated(conn: &SqliteConnection) -> QueryResult<Vec<Area>> {
        areas::dsl::areas
            .filter(areas::state.eq(AreaState::Updated))
            .load(conn)
    }
    pub fn save(&self, conn: &SqliteConnection) -> QueryResult<usize> {
        let query = diesel::update(areas::table).set(self);
                let query_debug = diesel::debug_query::<diesel::sqlite::Sqlite, _>(&query);
        debug!("Executing query: {}", query_debug);
        query.execute(*&conn)
    }
}

pub fn finalize_area_creation(area: &str, conn: &SqliteConnection) -> QueryResult<usize> {
    let query = diesel::update(areas::table)
        .filter(areas::name.eq(&area))
        .set((
            areas::state.eq(AreaState::Updated),
            areas::updated_at.eq(now),
        ));
        query.execute(*&conn)
}

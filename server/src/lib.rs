#[macro_use]
extern crate rocket;
#[macro_use]
extern crate rocket_sync_db_pools;
#[macro_use]
extern crate log;
#[macro_use]
extern crate diesel;
#[macro_use]
extern crate diesel_migrations;
pub mod api_routes;
pub mod area;
pub mod background_tasks;
mod diff_utils;
mod error;
pub mod names_cache;
mod schema;
pub mod ui_routes;

use diesel::SqliteConnection;
pub use error::Error;
pub type Result<T> = core::result::Result<T, Error>;
embed_migrations!();

#[database("serverdb")]
pub struct DbConn(SqliteConnection);

pub fn run_migrations(conn: &SqliteConnection) -> Result<()> {
    embedded_migrations::run(conn).map_err(Error::from)
}

pub fn init_logging() {
    env_logger::Builder::from_env("FTS_LOG")
        .format_timestamp(None)
        .init();
}

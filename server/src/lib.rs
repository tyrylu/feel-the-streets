// Rocket related stuff
#![feature(proc_macro_hygiene, decl_macro)]
// We want to use the await syntax
#[macro_use]
extern crate rocket;
#[macro_use]
extern crate rocket_contrib;
#[macro_use]
extern crate log;
#[macro_use]
extern crate diesel;
#[macro_use]
extern crate diesel_migrations;

pub mod amqp_utils;
pub mod area;
pub mod area_messaging;
pub mod background_task;
pub mod background_task_constants;
pub mod background_task_delivery;
pub mod background_tasks;
pub mod datetime_utils;
mod diff_utils;
mod error;
pub mod routes;
mod schema;

use diesel::SqliteConnection;
pub use error::Error;
pub type Result<T> = core::result::Result<T, Error>;
embed_migrations!();

#[database("serverdb")]
pub struct DbConn(SqliteConnection);

pub fn run_migrations(
    conn: &SqliteConnection,
) -> Result<()> {
    embedded_migrations::run(conn).map_err(Error::from)
}

pub fn init_logging() {
    env_logger::Builder::from_env("FTS_LOG")
        .format_timestamp(None)
        .init();
}

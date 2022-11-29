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
use std::sync::{Arc, Mutex};
use tera::Tera;
use tracing_subscriber::prelude::*;

pub type Result<T> = core::result::Result<T, Error>;
embed_migrations!();

#[derive(Clone)]
pub struct AppState {
    pub db_conn: Arc<Mutex<SqliteConnection>>,
    pub templates: Tera
}

pub fn run_migrations(conn: &SqliteConnection) -> Result<()> {
    embedded_migrations::run(conn).map_err(Error::from)
}

pub fn init_logging() {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("FTS_LOG")
                .unwrap_or_else(|_| "info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();
}

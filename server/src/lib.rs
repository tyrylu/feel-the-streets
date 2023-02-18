#[macro_use]
extern crate log;
pub mod api_routes;
pub mod area;
pub mod background_tasks;
pub mod db;
mod diff_utils;
mod error;
pub mod names_cache;
pub mod ui_routes;

pub use error::Error;
use std::sync::{Arc, Mutex};
use tera::Tera;
use tracing_subscriber::prelude::*;

pub type Result<T> = core::result::Result<T, Error>;

#[derive(Clone)]
pub struct AppState {
    pub db_conn: Arc<Mutex<rusqlite::Connection>>,
    pub templates: Tera,
}

pub fn init_logging() {
    let filter_layer = tracing_subscriber::EnvFilter::new(
        std::env::var("FTS_LOG").unwrap_or_else(|_| "info".into()),
    );
    if std::env::var("INVOCATION_ID").is_ok() {
        tracing_subscriber::registry()
            .with(filter_layer)
            .with(tracing_subscriber::fmt::layer().without_time())
            .init();
    } else {
        tracing_subscriber::registry()
            .with(filter_layer)
            .with(tracing_subscriber::fmt::layer())
            .init();
    }
}

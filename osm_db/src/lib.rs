#[macro_use]
extern crate log;

#[macro_use]
extern crate serde;

#[macro_use]
extern crate lazy_static;

pub mod area_db;
pub mod entities_query;
pub mod entities_query_condition;
pub mod entity;
pub mod entity_metadata;
mod error;
mod file_finder;
pub mod semantic_change;
pub mod translation;
pub use crate::area_db::AreaDatabase;
pub use crate::error::Error;
pub use rusqlite::types::ToSql;

pub type Result<T> = core::result::Result<T, Error>;

pub mod area_db;
pub mod entities_query;
pub mod entities_query_condition;
mod entities_query_executor;
pub mod entity;
pub mod entity_metadata;
pub mod entity_relationship;
pub mod entity_relationship_kind;
mod error;
mod file_finder;
pub mod relationship_inference;
pub mod semantic_change;
pub mod translation;
pub use crate::area_db::AreaDatabase;
pub use crate::error::Error;
pub use rusqlite::types::ToSql;

pub type Result<T> = core::result::Result<T, Error>;

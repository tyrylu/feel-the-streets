#[macro_use]
extern crate log;

#[macro_use]
extern crate serde_derive;

#[macro_use]
extern crate lazy_static;

pub mod area_db;
pub mod entity;
mod entity_metadata;
pub mod semantic_change;
pub mod translation;
pub use crate::area_db::AreaDatabase;

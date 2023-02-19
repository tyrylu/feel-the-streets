pub type Result<T> = core::result::Result<T, Error>;

pub mod change;
mod change_iterator;
mod error;
pub mod object;
pub mod object_manager;
pub mod overpass_api;
mod raw_object;
pub mod replication;
mod utils;
pub use error::Error;
pub use smol_str::SmolStr;

pub fn area_id_to_osm_id(area_id: i64) -> String {
    format!("r{}", area_id - 3_600_000_000)
}
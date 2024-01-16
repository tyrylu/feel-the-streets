pub type Result<T> = core::result::Result<T, Error>;

mod boundary_rect;
pub mod change;
pub mod changeset;
mod error;
pub mod main_api;
pub mod object;
pub mod object_manager;
pub mod overpass_api;
mod raw_changeset;
mod raw_object;
pub mod replication;
mod utils;
pub use boundary_rect::BoundaryRect;
pub use error::Error;
pub use smol_str::SmolStr;
pub use utils::unnest_wkb_geometry;

pub fn area_id_to_osm_id(area_id: i64) -> String {
    format!("r{}", area_id - 3_600_000_000)
}

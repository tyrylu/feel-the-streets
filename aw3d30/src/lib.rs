mod coordinate_ops;
pub mod dataset;
mod dataset_naming;
pub mod elevation_map;
mod error;
mod tile;

pub type Result<T> = std::result::Result<T, error::Error>;
pub use crate::error::Error;

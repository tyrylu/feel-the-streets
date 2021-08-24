pub type Result<T> = core::result::Result<T, Error>;

pub mod change;
mod change_iterator;
mod error;
pub mod object;
pub mod object_manager;
mod utils;
mod overpass_api_server;
pub use error::Error;
pub use smol_str::SmolStr;

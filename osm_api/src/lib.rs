pub type Result<T> = core::result::Result<T, Error>;

pub mod change;
mod change_iterator;
mod error;
pub mod object;
pub mod object_manager;
mod overpass_api_server;
mod utils;
pub use error::Error;
pub use smol_str::SmolStr;

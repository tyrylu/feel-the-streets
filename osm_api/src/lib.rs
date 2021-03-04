#[macro_use]
extern crate lazy_static;
#[macro_use]
extern crate serde;
#[macro_use]
extern crate log;

pub type Result<T> = core::result::Result<T, Error>;

pub mod change;
mod change_iterator;
mod error;
pub mod object;
pub mod object_manager;
mod utils;
pub use error::Error;
pub use smol_str::SmolStr;

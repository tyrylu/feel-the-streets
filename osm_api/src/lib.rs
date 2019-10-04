#[macro_use]
extern crate lazy_static;
#[macro_use]
extern crate serde;
#[macro_use]
extern crate log;

pub type Result<T> = core::result::Result<T, failure::Error>;

pub mod change;
mod change_iterator;
pub mod object;
pub mod object_manager;
mod utils;

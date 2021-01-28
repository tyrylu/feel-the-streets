#[macro_use] extern crate log;
mod context;
mod error;
pub use context::ZstdContext;
pub use error::Error;


pub type Result<T> = std::result::Result<T, Error>;
#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}

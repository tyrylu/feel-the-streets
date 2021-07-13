mod changes_batch;
pub mod changes_stream;
pub mod error;

pub type Result<T> = core::result::Result<T, error::Error>;
pub use changes_stream::ChangesStream;
pub use error::Error;

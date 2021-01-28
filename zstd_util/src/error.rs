#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Invalid return code from the ZSTD library: {0}")]
    ZSTDError(usize),
}

impl From<usize> for Error {
    fn from(val: usize) -> Error {
        Error::ZSTDError(val)
    }
}
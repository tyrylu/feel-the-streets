#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("The Zstd library returned an error: {0}")]
    ZSTDError(&'static str),
}

impl From<usize> for Error {
    fn from(val: usize) -> Error {
        Error::ZSTDError(zstd_safe::get_error_name(val))
    }
}

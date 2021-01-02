#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Unknown node type {0}")]
    UnknownNodeType(String),
    #[error("I/O error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Disk cache error: {0}")]
    DiskCacheError(#[from] rusqlite::Error),
    #[error("XML reading error: {0}")]
    XmlReaderError(#[from] xml::reader::Error),
    #[error("HTTP related error: {0}")]
    HttpError(String),
    #[error("WKB write error: {0}")]
    WKBWriteError(String),
    #[error("Serialization error: {0}")]
    SerializationError(#[from] bincode::Error),
    #[error("Invalid return code from the ZSTD library: {0}")]
    ZSTDError(usize)
}

impl From<usize> for Error {
    fn from(val: usize) -> Error {
        Error::ZSTDError(val)
    }
}
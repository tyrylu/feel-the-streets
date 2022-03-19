#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Unknown node type {0}")]
    UnknownNodeType(String),
    #[error("I/O error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Disk cache error: {0}")]
    DiskCacheError(#[from] sled::Error),
    #[error("XML reading error: {0}")]
    XmlReaderError(#[from] xml::reader::Error),
    #[error("HTTP related error: {0}")]
    HttpError(#[from] ureq::Error),
    #[error("WKB write error: {0}")]
    WKBWriteError(String),
    #[error("Serialization error: {0}")]
    SerializationError(#[from] bincode::Error),
    #[error("Zstd operation error: {0}")]
    ZstdError(#[from] zstd_util::Error),
    #[error("The retry limit was exceeded")]
    RetryLimitExceeded,
}

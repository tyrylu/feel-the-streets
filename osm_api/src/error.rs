#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Unknown node type {0}")]
    UnknownNodeType(String),
    #[error("I/O error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Disk cache error: {0}")]
    DiskCacheError(#[from] sled::Error),
    #[error("XML reading error: {0}")]
    XmlReaderError(#[from] quick_xml::Error),
    #[error("XML attribute conversion error: {0}")]
    XmlAttrError(#[from] quick_xml::events::attributes::AttrError),
    #[error("XML deserialization error: {0}")]
    XmlDeserializationError(#[from] quick_xml::de::DeError),
    #[error("HTTP related error: {0}")]
    HttpError(Box<ureq::Error>),
    #[error("WKB write error: {0}")]
    WKBWriteError(String),
    #[error("Serialization error: {0}")]
    SerializationError(#[from] bincode::Error),
    #[error("Zstd operation error: {0}")]
    ZstdError(#[from] zstd_util::Error),
    #[error("Replication API error: {0}")]
    ReplicationError(#[from] crate::replication::Error),
    #[error("The retry limit was exceeded")]
    RetryLimitExceeded,
    #[error("The passed object was not an OSM way")]
    NotAWay,
}

impl From<ureq::Error> for Error {
    fn from(value: ureq::Error) -> Self {
        Error::HttpError(Box::new(value))
    }
}
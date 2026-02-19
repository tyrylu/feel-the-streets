#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Unknown node type {0}")]
    UnknownNodeType(String),
    #[error("I/O error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Disk cache error: {0}")]
    DiskCacheError(#[from] redb::DatabaseError),
    #[error("Disk cache transaction error: {0}")]
    DiskCacheTransactionError(Box<redb::TransactionError>),
    #[error("Disk cache table error: {0}")]
    DiskCacheTableError(#[from] redb::TableError),
    #[error("Disk cache storage error: {0}")]
    DiskCacheStorageError(#[from] redb::StorageError),
    #[error("Disk cache commit error: {0}")]
    DiskCacheCommitError(#[from] redb::CommitError),
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
    SerializationError(#[from] bincode::error::EncodeError),
    #[error("Deserialization error: {0}")]
    DeserializationError(#[from] bincode::error::DecodeError),
    #[error("Zstd operation error: {0}")]
    ZstdError(#[from] zstd_util::Error),
    #[error("Replication API error: {0}")]
    ReplicationError(#[from] crate::replication::Error),
    #[error("The retry limit was exceeded")]
    RetryLimitExceeded,
    #[error("The passed object was not an OSM way")]
    NotAWay,
    #[error("The Overpass API returned an error: {0}")]
    OverpassAPIError(String),
}

impl From<ureq::Error> for Error {
    fn from(value: ureq::Error) -> Self {
        Error::HttpError(Box::new(value))
    }
}

impl From<redb::TransactionError> for Error {
    fn from(value: redb::TransactionError) -> Self {
        Error::DiskCacheTransactionError(Box::new(value))
    }
}   
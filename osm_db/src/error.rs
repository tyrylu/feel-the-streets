#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("OSM api error: {0}")]
    OsmApiError(#[from] osm_api::Error),
    #[error("Database error: {0}")]
    DbError(#[from] rusqlite::Error),
    #[error("I/O error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Serde error: {0}")]
    SerdeError(#[from] serde_json::error::Error),
    #[error("Zstd error: {0}")]
    ZstdError(#[from] zstd_util::Error),
    #[error("Attempted an application of a change type which should be never applied")]
    IllegalChangeType,
}

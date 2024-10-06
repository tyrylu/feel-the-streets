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
    #[error("Aw3d30 error: {0}")]
    Aw3d30Error(#[from] aw3d30::Error),
    #[error("Attempted an application of a change type which should be never applied")]
    IllegalChangeType,
}

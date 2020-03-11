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
}

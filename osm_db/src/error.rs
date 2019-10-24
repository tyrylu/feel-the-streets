#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("OSM api error: {0}")]
    OsmApiError(#[from] osm_api::Error),
    #[error("Database error: {0}")]
    DbError(#[from] rusqlite::Error)
}
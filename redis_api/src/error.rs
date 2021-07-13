use thiserror::Error;

#[derive(Debug, Error)]
pub enum Error {
    #[error("Redis error: {0}")]
    RedisError(#[from] redis::RedisError),
    #[error("OSM db error: {0}")]
    OSMDbError(#[from] osm_db::Error),
}

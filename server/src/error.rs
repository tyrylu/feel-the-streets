use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
};
use std::time::SystemTimeError;

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("I/O error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Rusqlite error: {0}")]
    RusqliteError(#[from] rusqlite::Error),
    #[error("Json error: {0}")]
    JsonError(#[from] serde_json::Error),
    #[error("Osm  database error: {0}")]
    OsmDbError(#[from] osm_db::Error),
    #[error("Osm API error: {0}")]
    OsmApiError(#[from] osm_api::Error),
    #[error("OSM replication API error: {0}")]
    OSMReplicationApiError(#[from] osm_api::replication::Error),
    #[error("Datetime parssing error: {0}")]
    DateTimeParseError(#[from] chrono::format::ParseError),
    #[error("Environment variable error: {0}")]
    EnvironmentVarError(#[from] std::env::VarError),
    #[error("Can not guarantee database integrity")]
    DatabaseIntegrityError,
    #[error("The given client is already created")]
    ClientAlreadyExists,
    #[error("Dotenv error: {0}")]
    DotenvError(#[from] dotenvy::Error),
    #[error("The system time is before the unix epoch: {0}")]
    SystemTimeError(#[from] SystemTimeError),
    #[error("Redis api error: {0}")]
    RedisApiError(#[from] redis_api::Error),
    #[error("Doitlater error: {0}")]
    DoItLaterError(#[from] doitlater::Error),
    #[error("Tera error: {0}")]
    TeraError(#[from] tera::Error),
    #[error("Failed to join a Tokio task: {0}")]
    JoinError(#[from] tokio::task::JoinError),
    #[error("Aw3d30 error: {0}")]
    Aw3d30Error(#[from] aw3d30::Error),
}

impl IntoResponse for Error {
    fn into_response(self) -> Response {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Something went wrong: {self}"),
        )
            .into_response()
    }
}

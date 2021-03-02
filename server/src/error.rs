use std::time::SystemTimeError;

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Migrations execution error: {0}")]
    MigrationsExecutionError(#[from] diesel_migrations::RunMigrationsError),
    #[error("I/O error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Diesel error: {0}")]
    DieselError(#[from] diesel::result::Error),
    #[error("Json error: {0}")]
    JsonError(#[from] serde_json::Error),
    #[error("Lapin error: {0}")]
    LapinError(#[from] lapin::Error),
    #[error("Diesel connection error: {0}")]
    DieselConnectionError(#[from] diesel::ConnectionError),
    #[error("Osm  database error: {0}")]
    OsmDbError(#[from] osm_db::Error),
    #[error("Osm API error: {0}")]
    OsmApiError(#[from] osm_api::Error),
    #[error("Datetime parssing error: {0}")]
    DateTimeParseError(#[from] chrono::format::ParseError),
    #[error("Environment variable error: {0}")]
    EnvironmentVarError(#[from] std::env::VarError),
    #[error("Can not guarantee database integrity")]
    DatabaseIntegrityError,
    #[error("Dotenv error: {0}")]
    DotenvError(#[from] dotenv::Error),
    #[error("The system time is before the unix epoch: {0}")]
    SystemTimeError(#[from] SystemTimeError),
}

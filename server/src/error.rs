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
    #[error("The given client is already created")]
    ClientAlreadyExists,
    #[error("Dotenv error: {0}")]
    DotenvError(#[from] dotenv::Error),
    #[error("The system time is before the unix epoch: {0}")]
    SystemTimeError(#[from] SystemTimeError),
    #[error("Redis api error: {0}")]
    RedisApiError(#[from] redis_api::Error),
    #[error("Doitlater error: {0}")]
    DoItLaterError(#[from] doitlater::Error),
}

impl<'r, 'o> rocket::response::Responder<'r, 'o> for Error
where
    'o: 'r,
{
    fn respond_to(self, request: &'r rocket::Request<'_>) -> rocket::response::Result<'o> {
        let msg = format!("{}", self);
        rocket::response::status::Custom(
            rocket::http::Status::InternalServerError,
            rocket::response::content::Plain(msg),
        )
        .respond_to(request)
    }
}

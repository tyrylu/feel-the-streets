use chrono::DateTime;
use server::{background_tasks::area_db_creation, Result};
use std::env;

fn main() -> Result<()> {
    let _dotenv_path = dotenvy::dotenv()?;
    server::init_logging();
    let time = env::args().nth(2).map(|t| Some(DateTime::parse_from_rfc3339(&t).expect("If provided, it must be a RFC 3339 date"))).unwrap_or(None);
    area_db_creation::create_area_database(
        env::args()
            .nth(1)
            .unwrap()
            .parse()
            .expect("Should be an i64"),
            time,
    )?;
    Ok(())
}

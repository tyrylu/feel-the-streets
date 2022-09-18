extern crate server;
use server::{background_tasks::area_db_creation, Result};
use std::env;

fn main() -> Result<()> {
    let _dotenv_path = dotenvy::dotenv()?;
    server::init_logging();
    area_db_creation::create_area_database(
        env::args()
            .nth(1)
            .unwrap()
            .parse()
            .expect("Should be an i64"),
    )?;
    Ok(())
}

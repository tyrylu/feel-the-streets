extern crate server;
use server::{background_tasks::area_db_update, Result};

fn main() -> Result<()> {
    let _dotenv_path = dotenvy::dotenv()?;
    server::init_logging();
    area_db_update::update_area_databases()?;
    Ok(())
}

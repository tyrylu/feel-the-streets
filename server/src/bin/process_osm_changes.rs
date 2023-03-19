extern crate server;
use server::{background_tasks::osm_changes_processing, Result};
use std::env;

fn main() -> Result<()> {
    let _dotenv_path = dotenvy::dotenv()?;
    server::init_logging();
    osm_changes_processing::process_osm_changes(
        env::args()
            .nth(1)
            .unwrap()
            .parse()
            .expect("Should be an i64"),
    )?;
    Ok(())
}

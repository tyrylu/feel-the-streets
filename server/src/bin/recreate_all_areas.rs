extern crate server;
use diesel::{Connection, SqliteConnection};
use server::{area::Area, background_tasks::area_db_creation, Result};
use std::fs;
use std::path::Path;
use std::time::Instant;

fn main() -> Result<()> {
    let _dotenv_path = dotenv::dotenv()?;
    server::init_logging();
    let server_conn = SqliteConnection::establish("server.db")?;
    for area in Area::all(&server_conn)? {
        let area_file = format!("{}.db", area.osm_id);
        if Path::new(&area_file).exists() {
            fs::remove_file(&area_file)?;
        }
        println!("Recreating area {}...", area.name);
        let start = Instant::now();
        area_db_creation::create_area_database(area.osm_id)?;
        println!("Area created in {:?}", start.elapsed());
    }
    Ok(())
}

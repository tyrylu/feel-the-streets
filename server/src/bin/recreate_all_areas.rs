extern crate server;
use server::{background_tasks::area_db_creation, Result, area::Area};
use std::time::Instant;
use diesel::{Connection, SqliteConnection};

fn main() -> Result<()> {
    server::init_logging();
    let server_conn = SqliteConnection::establish("server.db")?;
    for area in Area::all(&server_conn)? {
        println!("Recreating area {}...", area.name);
    let start = Instant::now();
    area_db_creation::create_area_database(&area.name)?;
    println!("Area created in {:?}", start.elapsed());
    }
        Ok(())
}

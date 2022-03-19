use diesel::{Connection, SqliteConnection};
use osm_api::object_manager::OSMObjectManager;
use server::{area::Area, Result};
use std::sync::{Arc, Mutex};

fn main() -> Result<()> {
    let _dotenv_path = dotenv::dotenv()?;
    server::init_logging();
    let area_db_conn = Arc::new(Mutex::new(SqliteConnection::establish("server.db")?));
    let area_id: i64 = std::env::args()
        .nth(1)
        .expect("Area id not provided")
        .parse()
        .expect("Area id not an int");
    let area = Area::find_by_osm_id(area_id, &area_db_conn.lock().unwrap())?;
    let _record = server::background_tasks::area_db_update::update_area(area, area_db_conn, OSMObjectManager::new()?)?;
    Ok(())
}

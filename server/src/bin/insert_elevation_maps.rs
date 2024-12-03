use log::info;
use osm_db::AreaDatabase;
use server::{area::Area, background_tasks::area_db_creation, db, Result};
use std::fs;

fn main() -> Result<()> {
    let _dotenv_path = dotenvy::dotenv()?;
    server::init_logging();
    let db_conn = db::connect_to_server_db()?;
    for mut area in Area::all(&db_conn)? {
        let bounds = area.bounds(&db_conn)?;
        info!(
            "Getting elevation map for {}, bounds: {:?}",
            area.name, bounds
        );
        let elevation_map = area_db_creation::elevation_map_for_bounds(&bounds)?;
        let area_db = AreaDatabase::open_existing(area.osm_id, true)?;
        area_db.replace_elevation_map(&elevation_map)?;
        let size = fs::metadata(AreaDatabase::path_for(area.osm_id, true))?.len();
        area.db_size = size as i64;
        area.save(&db_conn)?;
    }
    Ok(())
}

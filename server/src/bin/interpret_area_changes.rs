use osm_api::object_manager::OSMObjectManager;
use osm_api::Result;
use std::env;
use chrono::{DateTime, Utc};

fn main() -> Result<()> {
    server::init_logging();
    let ts = DateTime::parse_from_rfc3339(&env::args().nth(2).unwrap())?.with_timezone(&Utc);
        let manager = OSMObjectManager::new();
    for change in manager.lookup_differences_in(&env::args().nth(1).unwrap(), &ts)? {
        let change = change?;
        println!("Got change {:?}", change);
    }
    Ok(())
}
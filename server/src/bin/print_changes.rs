use chrono::{DateTime, Utc};
use osm_api::object_manager::OSMObjectManager;
use std::env;

fn main() {
    let _dotenv_path = dotenv::dotenv().expect("Dotenv initialization failed");
    server::init_logging();
    let id: i64 = env::args()
        .nth(1)
        .expect("Area id is required")
        .parse()
        .expect("Area id must be an u64");
    let after =
        DateTime::parse_from_rfc3339(&env::args().nth(2).expect("The after time is required"))
            .expect("It must be an RFC 3339 datetime")
            .with_timezone(&Utc);
    let manager = OSMObjectManager::new().expect("Could not create OSMObjectManager");
    for change in manager
        .lookup_differences_in(id, &after)
        .expect("Could not lookup changes")
    {
        let change = change.expect("No change");
        let obj = change.old.as_ref().unwrap_or_else(|| change.new.as_ref().expect(&format!("No old or new for change {:?}", change)));
        let geom = manager.get_geometry_as_wkb(&obj).expect("Could not get geom").expect(&format!("Geometry for {:?} was none.", obj));
        println!("{:?}, geom len: {}", change, geom.len());
    }
}

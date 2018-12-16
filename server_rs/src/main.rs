use osm_api::object_manager::OSMObjectManager;
use std::env;
fn main() {
    env_logger::init();
    let area = env::args()
        .nth(1)
        .expect("Provide the area, please.")
        .clone();
    let manager = OSMObjectManager::new();
    manager.lookup_objects_in(&area).expect("Lookup fail");
    for obj in manager.cached_objects() {
        let _translated = osm_db::translation::translator::translate(&obj, &manager)
            .expect("Failed to translate");
    }
}

use osm_api::object_manager::OSMObjectManager;
use std::env;
use std::fs;

fn main() -> osm_api::Result<()> {
    let id = env::args().nth(1).expect("Object id required");
    let manager = OSMObjectManager::new()?;
    let obj = manager.get_object(&id)?.expect("Could not get object");
    let geom = manager
        .get_geometry_of(&obj)?
        .expect("Could not create geometry");
    fs::write(
        format!("{}_geom.txt", obj.unique_id()),
        format!("{geom:#?}"),
    )?;
    let wkb = wkb::geom_to_wkb(&geom).expect("Could not create WKB representation");
    fs::write(format!("{}_geom.wkb", obj.unique_id()), wkb)?;
    println!("Successfully saved.");
    Ok(())
}

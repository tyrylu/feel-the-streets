use osm_api::BoundaryRect;
use osm_api::object_manager::OSMObjectManager;
use std::env;
use std::fs;

fn main() -> osm_api::Result<()> {
    let id = env::args().nth(1).expect("Object id required");
    let bounds = if env::args().count() == 6 {
        BoundaryRect {
            min_x: env::args().nth(2).expect("Min x must be provided").parse().expect("Min x must be a float"),
            min_y: env::args().nth(3).expect("Min y must be provided").parse().expect("Min y must be a float"),
            max_x: env::args().nth(4).expect("Max x must be provided").parse().expect("Max x must be a float"),
            max_y: env::args().nth(5).expect("Max y must be provided").parse().expect("Max y must be a float"),
        }
    }
    else {
        BoundaryRect::whole_world()
    };
    let manager = OSMObjectManager::new()?;
    println!("Getting geometry for {id} in bounds: {bounds:?}");
    let obj = manager.get_object(&id)?.expect("Could not get object");
    let geom = manager
        .get_geometry_of(&obj, &bounds)?
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

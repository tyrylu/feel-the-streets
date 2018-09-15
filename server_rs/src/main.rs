#[macro_use]
extern crate lazy_static;
#[macro_use]
extern crate error_chain;
#[macro_use]
extern crate serde_derive;
#[macro_use]
extern crate log;
extern crate itertools;
extern crate reqwest;
extern crate rusqlite;
extern crate serde;
extern crate serde_json;
extern crate sqlitemap;

mod osm;
fn main() -> osm::error::Result<()> {
    let mut mgr = osm::object_manager::OSMObjectManager::new();
    mgr.lookup_objects_in("Praha")?;
    let o = mgr.get_object("n13475344")?;
    
    Ok(())
}

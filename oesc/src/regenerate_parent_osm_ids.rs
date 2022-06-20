use anyhow::Result;
use diesel::{Connection, SqliteConnection};
use osm_api::object_manager::OSMObjectManager;
use server::area::Area;
use server::background_tasks::area_db_creation;
use server::names_cache::OSMObjectNamesCache;

pub(crate) fn regenerate_parent_osm_ids() -> Result<()> {
    let conn = SqliteConnection::establish("server.db")?;
    let manager = OSMObjectManager::new()?;
    let mut cache = OSMObjectNamesCache::load()?;
    for mut area in Area::all(&conn)? {
        println!("Regenerating parent osm ids for {}...", area.name);
        let parent_ids_str = area_db_creation::get_parent_ids_str_for(area.osm_id, &manager, &mut cache)?;
        area.parent_osm_ids = Some(parent_ids_str);
        area.save(&conn)?;
    }
    println!("All areas processed successfully.");
    cache.save()?;
    Ok(())
}

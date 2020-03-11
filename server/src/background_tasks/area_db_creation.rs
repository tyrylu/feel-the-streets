use crate::area;
use crate::Result;
use diesel::{Connection, SqliteConnection};
use osm_api::object_manager::{self, OSMObjectManager};
use osm_db::area_db::AreaDatabase;
use osm_db::translation::{record::TranslationRecord, translator};

pub fn create_area_database(area: i64) -> Result<()> {
    info!("Starting to create area with id {}.", area);
    let manager = OSMObjectManager::new();
    let mut record = TranslationRecord::new();
    manager.lookup_objects_in(area)?;
    let mut cache = manager.get_cache();
    let mut db = AreaDatabase::create(area)?;
    db.insert_entities(
        object_manager::cached_objects_in(&mut cache).filter_map(|obj| {
            translator::translate(&obj, &manager, &mut record).expect("Translation failure.")
        }),
    )?;
    let area_db_conn = SqliteConnection::establish("server.db")?;
    area::finalize_area_creation(area, &area_db_conn)?;
    record.save_to_file(&format!("creation_{}.json", area))?;
    info!("Area created successfully.");
    Ok(())
}

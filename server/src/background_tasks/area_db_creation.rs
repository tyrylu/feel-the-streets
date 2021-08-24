use crate::area;
use crate::Result;
use diesel::{Connection, SqliteConnection};
use osm_api::object_manager::{self, OSMObjectManager};
use osm_db::area_db::AreaDatabase;
use osm_db::relationship_inference::infer_additional_relationships_for;
use osm_db::translation::{record::TranslationRecord, translator};
use serde::{Deserialize, Serialize};

pub fn create_area_database(area: i64) -> Result<()> {
    info!("Starting to create area with id {}.", area);
    let manager = OSMObjectManager::new()?;
    let mut record = TranslationRecord::new();
    manager.lookup_objects_in(area)?;
    let mut cache = manager.get_cache();
    let from_network_ids = manager.get_ids_retrieved_from_network();
    let mut db = AreaDatabase::create(area)?;
    db.insert_entities(
        object_manager::cached_objects_in(&mut cache).filter_map(|obj| {
            if !from_network_ids.contains(&obj.unique_id()) {
                return None;
            }
            translator::translate(&obj, &manager, &mut record).expect("Translation failure.")
        }),
    )?;
    db.begin()?;
    infer_additional_relationships_for(&db)?;
    db.commit()?;
    let area_db_conn = SqliteConnection::establish("server.db")?;
    area::finalize_area_creation(area, &area_db_conn)?;
    record.save_to_file(&format!("creation_{}.json", area))?;
    info!("Area created successfully.");
    Ok(())
}

#[derive(Serialize, Deserialize)]
pub struct CreateAreaDatabaseTask {
    area_id: i64,
}

impl CreateAreaDatabaseTask {
    pub fn new(area_id: i64) -> Self {
        Self { area_id }
    }
}

#[typetag::serde]
impl doitlater::Executable for CreateAreaDatabaseTask {
    fn execute(&self) -> std::result::Result<(), Box<dyn std::error::Error>> {
        create_area_database(self.area_id).map_err(|e| Box::new(e) as Box<dyn std::error::Error>)
    }
}

use crate::area;
use crate::Result;
use crate::names_cache::OSMObjectNamesCache;
use diesel::{Connection, SqliteConnection};
use osm_api::SmolStr;
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
    let parent_ids_str = get_parent_ids_str_for(area, &manager)?;
    let area_db_conn = SqliteConnection::establish("server.db")?;
    area::finalize_area_creation(area, parent_ids_str, &area_db_conn)?;
    record.save_to_file(&format!("creation_{}.json", area))?;
    info!("Area created successfully.");
    Ok(())
}

pub fn get_parent_ids_str_for(area: i64, manager: &OSMObjectManager) -> Result<String> {
        let mut parents = manager.get_area_parents(area)?;
    info!("Found {} administrative parent candidates.", parents.len());
    parents.retain(|p| p.tags.contains_key("admin_level"));
    info!("After filtering, {} candidates remained.", parents.len());
    parents.sort_by_key(|p| p.tags["admin_level"].clone());
    let mut cache = OSMObjectNamesCache::load()?;
    for parent in &parents {
        cache.cache_names_of(parent);
    }
    cache.save()?;
    Ok(parents.iter().map(|p|p.unique_id()).collect::<Vec<SmolStr>>().join(","))
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

use crate::names_cache::OSMObjectNamesCache;
use crate::Result;
use crate::{
    area,
    db::{self, Connection},
};
use doitlater::typetag;
use osm_api::BoundaryRect;
use osm_api::object_manager::OSMObjectManager;
use osm_api::SmolStr;
use osm_db::area_db::AreaDatabase;
use osm_db::relationship_inference::infer_additional_relationships_for;
use osm_db::translation::{record::TranslationRecord, translator};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};

pub fn create_area_database(area: i64) -> Result<()> {
    let manager = OSMObjectManager::new()?;
    let area_db_conn = Arc::new(Mutex::new(db::connect_to_server_db()?));
    let cache = Arc::new(Mutex::new(OSMObjectNamesCache::load()?));
    create_area_database_worker(area, manager, area_db_conn, cache.clone())?;
    cache.lock().unwrap().save()?;
    Ok(())
}

pub fn create_area_database_worker(
    area: i64,
    manager: OSMObjectManager,
    area_db_conn: Arc<Mutex<Connection>>,
    cache: Arc<Mutex<OSMObjectNamesCache>>,
) -> Result<()> {
    info!("Starting to create area with id {}.", area);
    let mut record = TranslationRecord::new();
    manager.lookup_objects_in(area)?;
    let area_object = manager.get_object(&osm_api::area_id_to_osm_id(area))?.expect("Area object not found");
    let area_geom = manager.get_geometry_as_wkb(&area_object, &BoundaryRect::whole_world())?.unwrap();
    let area_bounds = db::get_geometry_bounds(&area_db_conn.lock().unwrap(), &area_geom)?;
    info!("Using area bounds: {:?}", area_bounds);
    let from_network_ids = manager.get_ids_retrieved_from_network();
    let mut area_db = AreaDatabase::create(area)?;
    let mut newest_timestamp = "2000-01-01T00:00:00Z".to_string();
    area_db.insert_entities(manager.cached_objects().filter_map(|obj| {
        if !from_network_ids.contains(&obj.unique_id()) {
            return None;
        }
        let entity = translator::translate(&obj, &area_bounds, &manager, &mut record).expect("Translation failure.");
        if let Some(ent) = &entity {
            let ts_clone = newest_timestamp.clone();
            newest_timestamp= ts_clone.max(obj.timestamp.clone());
            db::insert_area_entity(&area_db_conn.lock().unwrap(), area, &ent.0.id).expect("Could not insert entity to the entities summary table");
            db::insert_entity_geometry_parts(&area_db_conn.lock().unwrap(), &manager, &obj).expect("Could not insert object geometry parts");
        }
        entity
    }))?;
    drop(from_network_ids);
    area_db.begin()?;
    infer_additional_relationships_for(&area_db)?;
    area_db.commit()?;
    let parent_ids_str = get_parent_ids_str_for(area, &manager, &mut cache.lock().unwrap())?;
    area::finalize_area_creation(area, parent_ids_str, &area_geom, &newest_timestamp, &mut area_db_conn.lock().unwrap())?;
    record.save_to_file(&format!("creation_{area}.json"))?;
    info!("Area {} created successfully.", area);
    Ok(())
}

pub fn get_parent_ids_str_for(
    area: i64,
    manager: &OSMObjectManager,
    cache: &mut OSMObjectNamesCache,
) -> Result<String> {
    let mut parents = manager.get_area_parents(area)?;
    info!(
        "Found {} administrative parent candidates for area {}.",
        parents.len(),
        area
    );
    parents.retain(|p| p.tags.contains_key("admin_level"));
    info!(
        "After filtering, {} candidates for area {} remained.",
        parents.len(),
        area
    );
    parents.sort_by_key(|p| {
        if p.tags["admin_level"].len() == 1 {
            format!("0{}", p.tags["admin_level"])
        } else {
            p.tags["admin_level"].clone()
        }
    });
    for parent in &parents {
        cache.cache_names_of(parent);
    }
    Ok(parents
        .iter()
        .map(|p| p.unique_id())
        .collect::<Vec<SmolStr>>()
        .join(","))
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

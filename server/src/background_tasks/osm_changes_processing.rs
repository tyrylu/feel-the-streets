use crate::Result;
use crate::area::Area;
use crate::db;
use doitlater::typetag;
use osm_api::BoundaryRect;
use osm_api::object::OSMObject;
use osm_api::object_manager::OSMObjectManager;
use osm_api::replication::{ReplicationApiClient, SequenceNumber};
use osm_api::main_api::MainAPIClient;
use osm_db::translation::{record::TranslationRecord, translator};
use rusqlite::Connection;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Serialize, Deserialize)]
pub struct ProcessOSMChangesTask;

#[typetag::serde]
impl doitlater::Executable for ProcessOSMChangesTask {
    fn execute(&self) -> std::result::Result<(), Box<dyn std::error::Error>> {
        run_osm_changes_processing().map_err(|e| Box::new(e) as Box<dyn std::error::Error>)
    }
}

fn run_osm_changes_processing() -> Result<()> {
    info!("Starting periodic OSM change processing.");
    let initial_sn = 5_000_000;
    process_osm_changes(initial_sn)?;
    Ok(())
}

pub fn process_osm_changes(initial_sn: u32) -> Result<()> {
    let r_client = ReplicationApiClient::default();
    let m_client = MainAPIClient::default();
    let latest_state = r_client.latest_replication_state()?;
    info!(
        "Processing OSM changes from {initial_sn} to {}",
        latest_state.sequence_number.0
    );
    let manager = OSMObjectManager::new()?;
    let server_db = db::connect_to_server_db()?;
    for sn in initial_sn..=latest_state.sequence_number.0 {
        process_osm_change(sn, &r_client, &m_client, &manager, &server_db)?;
    }
    Ok(())
}

fn process_osm_change(sn: u32, r_client: &ReplicationApiClient, m_client: &MainAPIClient, manager: &OSMObjectManager, server_db: &Connection) -> Result<()> {
        let mut changeset_interests = HashMap::new();
    let change = r_client.get_change(SequenceNumber::from_u32(sn)?)?;
    let newest_timestamp = db::newest_osm_object_timestamp(server_db)?;
    let mut record = TranslationRecord::new();
    for modified in &change.modify {
        if changeset_is_recent_enough(modified.changeset, &modified.timestamp, &newest_timestamp, &mut changeset_interests) && changeset_might_be_interesting(modified.changeset, &mut changeset_interests, m_client, server_db) {
            handle_modification(modified, manager, server_db, &mut record)?;
        }
        else {
                        continue;
        }
    }
    for created in &change.create {
        if changeset_is_recent_enough(created.changeset, &created.timestamp, &newest_timestamp, &mut changeset_interests) && changeset_might_be_interesting(created.changeset, &mut changeset_interests, m_client, server_db) {
            handle_creation(created, manager, server_db, &mut record)?;
        }
        else {
                        continue;
        }
    }
    for deleted in &change.delete {
        if changeset_is_recent_enough(deleted.changeset, &deleted.timestamp, &newest_timestamp, &mut changeset_interests) && changeset_might_be_interesting(deleted.changeset, &mut changeset_interests, m_client, server_db) {
            handle_deletion(deleted, server_db)?;
        }
        else {
                        continue;
        }
    }
    info!("Processed OSM change {} with {} created, {} modified, and {} deleted objects.", sn, change.create.len(), change.modify.len(), change.delete.len());
    Ok(())
}

fn changeset_is_recent_enough(changeset: u64, changeset_time: &str, newest_time: &str, changeset_interests: &mut HashMap<u64, bool>) -> bool {
    *changeset_interests.entry(changeset).or_insert_with(|| {
        changeset_time > newest_time
    })
}

fn changeset_might_be_interesting(changeset: u64, changeset_interests: &mut HashMap<u64, bool>, m_api: &MainAPIClient, conn: &Connection) -> bool {
    *changeset_interests.entry(changeset).or_insert_with(|| {
        debug!("Getting information about changeset {}", changeset);
        let changeset = m_api.get_changeset(changeset).expect("Could not get changeset");
        if let Some(bounds) = changeset.bounds {
            !Area::all_containing(conn, &bounds.as_wkb_polygon()).expect("Could not get areas containing the given bounds").is_empty()
        } else {
            true
        }
    })
}

fn handle_modification(object: &OSMObject, manager: &OSMObjectManager, conn: &Connection, record: &mut TranslationRecord) -> Result<()> {
    let areas = Area::all_containing(conn, &manager.get_geometry_as_wkb(object, &BoundaryRect::whole_world())?.unwrap())?;
    let geometric_containing_area_ids: Vec<i64> = areas.iter().map(|a| a.osm_id).collect();
    let db_containing_area_ids = db::areas_containing(&object.unique_id(), conn)?;
    for area in areas {
        let bounds = db::get_geometry_bounds(conn, &area.geometry.unwrap())?;
        if let Some((new_entity, new_related_ids)) = translator::translate(object, &bounds, manager, record)? {
            if db_containing_area_ids.contains(&area.osm_id) {
                info!("Object {} was modified in area {}.", new_entity.id, area.osm_id);
            }
            else {
                info!("Due to a modification of object {}, it now should be also in area {}", new_entity.id, area.osm_id);
            }
        }
    }
    for area_id in db_containing_area_ids {
        if !geometric_containing_area_ids.contains(&area_id) {
            info!("Object {} is no longer part of area {}.", object.unique_id(), area_id);
        }
    }
    for parent_entity_id in db::entities_containing(&object.unique_id(), conn)? {
        info!("Because of a change of {}, we need to recalculate the geometry of {parent_entity_id}.", object.unique_id());
    }
    Ok(())
}

fn handle_creation(object: &OSMObject, manager: &OSMObjectManager, conn: &Connection, record: &mut TranslationRecord) -> Result<()> {
    let areas = Area::all_containing(conn, &manager.get_geometry_as_wkb(object, &BoundaryRect::whole_world())?.unwrap())?;
    if areas.is_empty() {
        return Ok(())
    }
    for area in areas {
        let bounds = db::get_geometry_bounds(conn, &area.geometry.unwrap())?;
        if let Some((entity, related_ids)) = translator::translate(object, &bounds, manager, record)? {
            info!("Object {} was created in area {}.", entity.id, area.osm_id);
        }
    }
    Ok(())
}

fn handle_deletion(object: &OSMObject, conn: &Connection) -> Result<()> {
       let area_ids = db::areas_containing(&object.unique_id(), conn)?;
       if area_ids.is_empty() {
        return Ok(())
       }
       info!("Object {} was deleted in {:?}", object.unique_id(), area_ids);
       Ok(())
    }
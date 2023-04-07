use crate::Result;
use crate::area::Area;
use crate::db;
use doitlater::typetag;
use osm_api::BoundaryRect;
use osm_api::object::OSMObject;
use osm_api::object_manager::OSMObjectManager;
use osm_api::replication::{ReplicationApiClient, SequenceNumber};
use osm_api::main_api::MainAPIClient;
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
    for sn in initial_sn..=latest_state.sequence_number.0 {
        process_osm_change(sn, &r_client, &m_client, &manager)?;
    }
    Ok(())
}

fn process_osm_change(sn: u32, r_client: &ReplicationApiClient, m_client: &MainAPIClient, manager: &OSMObjectManager) -> Result<()> {
    let mut server_db = db::connect_to_server_db()?;
    let mut changeset_interests = HashMap::new();
    let change = r_client.get_change(SequenceNumber::from_u32(sn)?)?;
    for modified in &change.modify {
        if changeset_might_be_interesting(modified.changeset, &mut changeset_interests, m_client, &mut server_db) {
            handle_modification(modified, manager, &mut server_db)?;
        }
        else {
                        continue;
        }
    }
    for created in &change.create {
        if changeset_might_be_interesting(created.changeset, &mut changeset_interests, m_client, &mut server_db) {
            handle_creation(created, manager, &mut server_db)?;
        }
        else {
                        continue;
        }
    }
    for deleted in &change.delete {
        if changeset_might_be_interesting(deleted.changeset, &mut changeset_interests, m_client, &mut server_db) {
            handle_deletion(deleted, manager, &mut server_db)?;
        }
        else {
                        continue;
        }
    }
    info!("Processed OSM change {} with {} created, {} modified, and {} deleted objects.", sn, change.create.len(), change.modify.len(), change.delete.len());
    Ok(())
}

fn changeset_might_be_interesting(changeset: u64, changeset_interests: &mut HashMap<u64, bool>, m_api: &MainAPIClient, conn: &mut Connection) -> bool {
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

fn handle_modification(object: &OSMObject, manager: &OSMObjectManager, conn: &mut Connection) -> Result<()> {
    let areas = Area::all_containing(conn, &manager.get_geometry_as_wkb(object, &BoundaryRect::whole_world())?.unwrap())?;
    if areas.is_empty() {
        return Ok(())
    }
    info!("Object {} changed at least in {}.", object.unique_id(), areas[0].name);
    Ok(())
}

fn handle_creation(object: &OSMObject, manager: &OSMObjectManager, conn: &mut Connection) -> Result<()> {
    let areas = Area::all_containing(conn, &manager.get_geometry_as_wkb(object, &BoundaryRect::whole_world())?.unwrap())?;
    if areas.is_empty() {
        return Ok(())
    }
    info!("Object {} was created in {}.", object.unique_id(), areas[0].name);
    Ok(())
}

fn handle_deletion(object: &OSMObject, manager: &OSMObjectManager, conn: &mut Connection) -> Result<()> {
    if let Some(geom) = manager.get_geometry_as_wkb(object, &BoundaryRect::whole_world())? {
    let areas = Area::all_containing(conn, &geom)?;
    if areas.is_empty() {
        return Ok(())
    }
    info!("Object {} was deleted in {}.", object.unique_id(), areas[0].name);
} else {
    warn!("Can not determine whether object {} has any occurrences, it has no geometry.", object.unique_id());
}
    Ok(())
}
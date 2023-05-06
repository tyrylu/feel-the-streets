mod semantic_changes_container;
mod state_tracking;

use crate::area::{Area, AreaState};
use crate::db;
use crate::diff_utils::{self, ListChange};
use crate::Result;
use base64::prelude::*;
use doitlater::typetag;
use osm_api::main_api::MainAPIClient;
use osm_api::object::OSMObject;
use osm_api::object_manager::OSMObjectManager;
use osm_api::replication::{ReplicationApiClient, SequenceNumber};
use osm_api::BoundaryRect;
use osm_db::entity::Entity;
use osm_db::entity_relationship::RootedEntityRelationship;
use osm_db::entity_relationship_kind::EntityRelationshipKind;
use osm_db::relationship_inference;
use osm_db::semantic_change::{EntryChange, RelationshipChange, SemanticChange};
use osm_db::translation::{record::TranslationRecord, translator};
use osm_db::AreaDatabase;
use redis_api::ChangesStream;
use rusqlite::Connection;
use semantic_changes_container::SemanticChangesContainer;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::time::Instant;

#[derive(Serialize, Deserialize)]
pub struct ProcessOSMChangesTask;

#[typetag::serde]
impl doitlater::Executable for ProcessOSMChangesTask {
    fn execute(&self) -> std::result::Result<(), Box<dyn std::error::Error>> {
        run_osm_changes_processing().map_err(|e| Box::new(e) as Box<dyn std::error::Error>)
    }
}

fn run_osm_changes_processing() -> Result<()> {
    let initial_sn = state_tracking::read_latest_sequence_number()?;
    let latest_processed_sn = process_osm_changes(initial_sn)?;
    state_tracking::save_latest_sequence_number(latest_processed_sn)?;
    Ok(())
}

pub fn process_osm_changes(initial_sn: u32) -> Result<u32> {
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
    Ok(latest_state.sequence_number.0)
}

fn process_osm_change(
    sn: u32,
    r_client: &ReplicationApiClient,
    m_client: &MainAPIClient,
    manager: &OSMObjectManager,
    server_db: &Connection,
) -> Result<()> {
    let number = SequenceNumber::from_u32(sn)?;
    let newest_timestamp = db::newest_osm_object_timestamp(server_db)?;
    let info = r_client.get_change_info(&number)?;
    if info.timestamp <= newest_timestamp {
        info!("Not processing change {}, it is too old.", sn);
        return Ok(());
    }
    let mut changeset_interests = HashMap::new();
    let change = r_client.get_change(number)?;
    let mut record = TranslationRecord::new();
    let mut changes_container = SemanticChangesContainer::default();
    let mut interesting_modified = Vec::with_capacity(change.modify.len());
    for modified in &change.modify {
        if changeset_might_be_interesting(
            modified.changeset,
            &mut changeset_interests,
            m_client,
            server_db,
        ) {
            interesting_modified.push(modified);
        } else {
            continue;
        }
    }
    manager.ensure_has_cached_dependencies_for(&interesting_modified)?;
    for modified in interesting_modified {
        handle_modification(
            modified,
            manager,
            server_db,
            &mut record,
            &mut changes_container,
        )?;
    }
    let mut interesting_created = Vec::with_capacity(change.create.len());
    for created in &change.create {
        if changeset_might_be_interesting(
            created.changeset,
            &mut changeset_interests,
            m_client,
            server_db,
        ) {
            interesting_created.push(created);
        } else {
            continue;
        }
    }
    manager.ensure_has_cached_dependencies_for(&interesting_created)?;
    for created in interesting_created {
        handle_creation(
            created,
            manager,
            server_db,
            &mut record,
            &mut changes_container,
        )?;
    }
    for deleted in &change.delete {
        if changeset_might_be_interesting(
            deleted.changeset,
            &mut changeset_interests,
            m_client,
            server_db,
        ) {
            handle_deletion(deleted, server_db, manager, &mut changes_container)?;
        } else {
            continue;
        }
    }
    for (area_id, info) in changes_container.iter_mut() {
        info!(
            "Processing {} semantic changes for area {}.",
            info.changes.len(),
            area_id
        );
        let mut area = Area::find_by_osm_id(*area_id, server_db).expect("Area should exist");
        area.state = AreaState::ApplyingChanges;
        area.save(server_db)?;
        let mut area_db = AreaDatabase::open_existing(*area_id, true)?;
        area_db.begin()?;
        for change in &info.changes {
            area_db.apply_change(change)?;
        }
        area_db.apply_deferred_relationship_additions()?;
        infer_additional_relationships(&mut info.changes, &area_db)?;
        area_db.commit()?;
        let mut stream = ChangesStream::new_from_env(area.osm_id)?;
        if !stream.exists()? || !stream.should_publish_changes()? {
            info!(
                "Not publishing the changes of area {}, no clients or forced redownload.",
                area_id
            );
        } else {
            let prev_usage = stream.memory_usage()?;
            let collected = stream.garbage_collect()?;
            let current_usage = stream.memory_usage()?;
            if collected > 0 {
                info!("Garbage collection of the stream for area {} removed {} changes decreasing the memory usage of the stream from {} to {} bytes.", area.osm_id, collected, prev_usage, current_usage);
            }
            debug!(
                "Publishing {} changes for area {}...",
                info.changes.len(),
                area.osm_id
            );
            let mut batch = stream.begin_batch();
            for change in &info.changes {
                batch.add_change(change)?;
            }
            debug!("Changes for area {} published.", area.osm_id);
        }
        let size = fs::metadata(AreaDatabase::path_for(area.osm_id, true))?.len() as i64;
        area.db_size = size;
        area.newest_osm_object_timestamp = Some(info.newest_timestamp.to_string());
        if let Some(geom) = &info.geometry {
            area.geometry = Some(geom.clone());
        }
        area.state = AreaState::Updated;
        area.save(server_db)?;
    }
    info!(
        "Processed OSM change {} with {} created, {} modified, and {} deleted objects.",
        sn,
        change.create.len(),
        change.modify.len(),
        change.delete.len()
    );
    Ok(())
}

fn changeset_might_be_interesting(
    changeset: u64,
    changeset_interests: &mut HashMap<u64, bool>,
    m_api: &MainAPIClient,
    conn: &Connection,
) -> bool {
    *changeset_interests.entry(changeset).or_insert_with(|| {
        debug!("Getting information about changeset {}", changeset);
        let changeset = m_api
            .get_changeset(changeset)
            .expect("Could not get changeset");
        if let Some(bounds) = changeset.bounds {
            !Area::all_containing(conn, &bounds.as_wkb_polygon())
                .expect("Could not get areas containing the given bounds")
                .is_empty()
        } else {
            true
        }
    })
}

fn handle_modification<'a>(
    object: &'a OSMObject,
    manager: &OSMObjectManager,
    conn: &Connection,
    record: &mut TranslationRecord,
    changes: &mut SemanticChangesContainer<'a>,
) -> Result<()> {
    let start = Instant::now();
    let object_geom = manager.get_geometry_as_wkb(object, &BoundaryRect::whole_world())?;
    if object_geom.is_none() {
        warn!("Ignoring modification of object {}, it no longer has a geometry.", object.unique_id());
        return Ok(());
    }
    let object_geom = object_geom.unwrap();
    let areas = Area::all_containing(
        conn,
        &object_geom,
    )?;
    trace!(
        "All db areas containing the entity retrieved in {:? }, they are: {:?}",
        start.elapsed(),
        areas
    );
    let geometric_containing_area_ids: Vec<i64> = areas.iter().map(|a| a.osm_id).collect();
    let object_id = object.unique_id();
    let db_containing_area_ids = db::areas_containing(&object_id, conn)?;
    for area in areas {
        trace!(
            "During modification, Getting bounds of area with OSM id {}.",
            area.osm_id
        );
        let bounds = area.bounds(conn)?;
        if let Some((new_entity, new_related_ids)) =
            translator::translate(object, &bounds, manager, record)?
        {
            manager.cache_object(object);
            // TODO: Find a cheaper way of regenerating the geometric parts
            db::delete_entity_geometry_parts(conn, &object_id)?;
            db::insert_entity_geometry_parts(conn, manager, object)?;
            if db_containing_area_ids.contains(&area.osm_id) {
                debug!(
                    "Object {} was modified in area {}.",
                    new_entity.id, area.osm_id
                );
                let semantic_change = to_update_change(new_entity, new_related_ids, area.osm_id)?;
                if object.unique_id().as_str() == osm_api::area_id_to_osm_id(area.osm_id) {
                    if let SemanticChange::Update {
                        ref property_changes,
                        ..
                    } = semantic_change
                    {
                        for change in property_changes {
                            match change {
                                EntryChange::Update {
                                    ref key, new_value, ..
                                } if key == "geometry" => {
                                    changes.update_geometry_for(
                                        area.osm_id,
                                        BASE64_STANDARD
                                            .decode(new_value.as_str().unwrap())
                                            .expect("Could not decode"),
                                    );
                                }
                                _ => {}
                            }
                        }
                    }
                }
                changes.add_change(area.osm_id, semantic_change);
                changes.update_newest_timestamp_for(area.osm_id, &object.timestamp);
            } else {
                debug!(
                    "Due to a modification of object {}, it now should be also in area {}",
                    new_entity.id, area.osm_id
                );
                db::insert_area_entity(conn, area.osm_id, &new_entity.id)?;
                changes.add_change(area.osm_id, to_create_change(new_entity, new_related_ids));
                changes.update_newest_timestamp_for(area.osm_id, &object.timestamp)
            }
        }
    }
    for area_id in db_containing_area_ids {
        if !geometric_containing_area_ids.contains(&area_id) {
            debug!(
                "Object {} is no longer part of area {}.",
                object_id, area_id
            );
            db::delete_area_entity(conn, area_id, &object_id)?;
            changes.add_change(area_id, SemanticChange::removing(&object_id))
        }
    }
    if geometric_containing_area_ids.is_empty() {
        manager.remove_cached_object(&object_id)?;
        db::delete_entity_geometry_parts(conn, &object_id)?;
    }
    for parent_entity_id in db::entities_containing(&object.unique_id(), conn)? {
        debug!("Because of a geometry change of {}, we need to recalculate the geometry of {parent_entity_id}.", object.unique_id());
        handle_geometry_change(&parent_entity_id, conn, manager, changes)?;
    }
    Ok(())
}

fn handle_geometry_change(
    entity_id: &str,
    conn: &Connection,
    manager: &OSMObjectManager,
    changes: &mut SemanticChangesContainer,
) -> Result<()> {
    let object = manager
        .get_object(entity_id)?
        .expect("Modified object managed to disappear");
    for area_id in db::areas_containing(entity_id, conn)? {
        let old_geom = AreaDatabase::open_existing(area_id, true)?
            .get_entity(entity_id)?
            .expect("The summary says we have the entity, but it is not there")
            .geometry;
        let bounds = Area::bounds_of(area_id, conn)?;
        let new_geom = manager
            .get_geometry_as_wkb(&object, &bounds)?
            .expect("Could not create new geometry");
        let geom_change = EntryChange::updating(
            "geometry",
            BASE64_STANDARD.encode(&old_geom).into(),
            BASE64_STANDARD.encode(&new_geom).into(),
        );
        changes.add_change(
            area_id,
            SemanticChange::updating(entity_id, vec![geom_change], vec![], vec![]),
        );
        if entity_id == osm_api::area_id_to_osm_id(area_id) {
            changes.update_geometry_for(area_id, new_geom);
        }
    }
    Ok(())
}

fn handle_creation<'a>(
    object: &'a OSMObject,
    manager: &OSMObjectManager,
    conn: &Connection,
    record: &mut TranslationRecord,
    changes: &mut SemanticChangesContainer<'a>,
) -> Result<()> {
    let geom = manager.get_geometry_as_wkb(object, &BoundaryRect::whole_world())?;
    // Use an if-let when we require Rust 1.65 for some other reason
    if geom.is_none() {
        return Ok(());
    }
    let areas = Area::all_containing(conn, &geom.unwrap())?;
    if areas.is_empty() {
        return Ok(());
    }
    // It will be at least in one of the areas, co cache it
    manager.cache_object(object);
    for area in areas {
        let bounds = area.bounds(conn)?;
        if let Some((entity, related_ids)) =
            translator::translate(object, &bounds, manager, record)?
        {
            debug!("Object {} was created in area {}.", entity.id, area.osm_id);
            db::insert_area_entity(conn, area.osm_id, &entity.id)?;
            db::insert_entity_geometry_parts(conn, manager, object)?;
            changes.add_change(area.osm_id, to_create_change(entity, related_ids));
            changes.update_newest_timestamp_for(area.osm_id, &object.timestamp);
        }
    }
    Ok(())
}

fn handle_deletion(
    object: &OSMObject,
    conn: &Connection,
    manager: &OSMObjectManager,
    changes: &mut SemanticChangesContainer,
) -> Result<()> {
    let object_id = object.unique_id();
    let area_ids = db::areas_containing(&object_id, conn)?;
    if area_ids.is_empty() {
        return Ok(());
    }
    manager.remove_cached_object(&object_id)?;
    db::delete_entity_records(conn, &object_id)?;
    for aid in area_ids {
        debug!("Object {} was deleted in area {}", object_id, aid);
        changes.add_change(aid, SemanticChange::removing(&object_id));
    }
    Ok(())
}

fn to_create_change(entity: Entity, ids: impl Iterator<Item = String>) -> SemanticChange {
    SemanticChange::creating(
        entity.id.to_string(),
        entity.geometry,
        entity.discriminator.to_string(),
        entity.data,
        entity.effective_width,
        child_ids_to_rels(ids),
    )
}

fn to_update_change(
    new_entity: Entity,
    new_related_ids: impl Iterator<Item = String>,
    area_id: i64,
) -> Result<SemanticChange> {
    let area_db = AreaDatabase::open_existing(area_id, true)?;
    let old_entity = area_db
        .get_entity(&new_entity.id)?
        .expect("A modified entity is not in the db");
    let old_child_ids = area_db.get_entity_child_ids(&old_entity.id)?;
    let old_rels = child_ids_to_rels(old_child_ids.into_iter());
    let new_rels = child_ids_to_rels(new_related_ids);
    let raw_rel_changes = diff_utils::diff_lists(&old_rels, &new_rels);
    let rel_changes = raw_rel_changes
        .into_iter()
        .map(|c| match c {
            ListChange::Add(v) => RelationshipChange::adding(v),
            ListChange::Remove(v) => RelationshipChange::removing(v),
        })
        .collect();
    let (data_changes, property_changes) = diff_utils::diff_entities(&old_entity, &new_entity)?;
    Ok(SemanticChange::updating(
        &old_entity.id,
        property_changes,
        data_changes,
        rel_changes,
    ))
}

fn child_ids_to_rels(ids: impl Iterator<Item = String>) -> Vec<RootedEntityRelationship> {
    ids.map(|id| RootedEntityRelationship::new(&id, EntityRelationshipKind::OSMChild))
        .collect()
}

fn infer_additional_relationships(
    changes: &mut Vec<SemanticChange>,
    area_db: &AreaDatabase,
) -> Result<()> {
    let mut cache = HashMap::new();
    for idx in 0..changes.len() {
        if changes[idx].is_create() {
            let entity_id = changes[idx].osm_id().to_string();
            debug!(
                "Enriching tags after creation resulting from {:?}.",
                changes[idx]
            );
            let mut entity = area_db
                .get_entity(&entity_id)?
                .expect("Entity disappeared from a database");
            let relationships = relationship_inference::infer_additional_relationships_for_entity(
                &mut entity,
                area_db,
                &mut cache,
            )?;
            for relationship in relationships {
                let target = if relationship.parent_id == entity_id {
                    &mut changes[idx]
                } else {
                    find_or_create_suitable_change(changes, &relationship.parent_id, false)
                };
                target.add_rooted_relationship(RootedEntityRelationship::new(
                    relationship.child_id.as_str(),
                    relationship.kind,
                ));
            }
        } else if changes[idx].is_update() {
            let entity_id = changes[idx].osm_id().to_string();
            debug!(
                "Enriching relationships resulting from update {:?}",
                changes[idx]
            );
            let current_relationships = area_db.get_relationships_related_to(&entity_id)?;
            let mut entity = area_db.get_entity(&entity_id)?.expect("Entity disappeared");
            let new_relationships =
                relationship_inference::infer_additional_relationships_for_entity(
                    &mut entity,
                    area_db,
                    &mut cache,
                )?;
            let differences = diff_utils::diff_lists(&current_relationships, &new_relationships);
            for difference in differences {
                let (parent_id, change) = match difference {
                    ListChange::Add(v) => (
                        v.parent_id,
                        RelationshipChange::adding(RootedEntityRelationship::new(
                            v.child_id.as_str(),
                            v.kind,
                        )),
                    ),
                    ListChange::Remove(v) => (
                        v.parent_id,
                        RelationshipChange::removing(RootedEntityRelationship::new(
                            v.child_id.as_str(),
                            v.kind,
                        )),
                    ),
                };
                let target = if parent_id == entity_id {
                    &mut changes[idx]
                } else {
                    find_or_create_suitable_change(changes, &parent_id, true)
                };
                target.add_relationship_change(change);
            }
        }
    }
    Ok(())
}

fn find_or_create_suitable_change<'a>(
    changes: &'a mut Vec<SemanticChange>,
    parent_id: &str,
    updates_only: bool,
) -> &'a mut SemanticChange {
    if let Some(pos) = changes
        .iter()
        .position(|c| c.osm_id() == parent_id && !c.is_remove() && (!updates_only || c.is_update()))
    {
        &mut changes[pos]
    } else {
        changes.push(SemanticChange::updating(parent_id, vec![], vec![], vec![]));
        changes.last_mut().unwrap()
    }
}

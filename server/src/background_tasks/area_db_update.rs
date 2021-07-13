use crate::area::{Area, AreaState};
use crate::diff_utils;
use crate::diff_utils::ListChange;
use crate::Result;
use chrono::{DateTime, Utc};
use diesel::{Connection, SqliteConnection};
use osm_api::change::OSMObjectChangeType;
use osm_api::object_manager::OSMObjectManager;
use osm_db::semantic_change::SemanticChange;
use osm_db::translation::{record::TranslationRecord, translator};
use osm_db::{
    area_db::AreaDatabase, entity_relationship::RootedEntityRelationship,
    entity_relationship_kind::EntityRelationshipKind, relationship_inference,
    semantic_change::RelationshipChange,
};
use redis_api::ChangesStream;
use serde::{Deserialize, Serialize};
use std::{
    collections::{HashMap, HashSet},
    fs,
};

fn find_or_create_suitable_change<'a>(
    changes: &'a mut Vec<SemanticChange>,
    parent_id: &str,
    updates_only: bool,
) -> &'a mut SemanticChange {
    if let Some(pos) = changes.iter().position(|c| {
        c.osm_id().unwrap() == parent_id && !c.is_remove() && (!updates_only || c.is_update())
    }) {
        &mut changes[pos]
    } else {
        changes.push(SemanticChange::updating(parent_id, vec![], vec![], vec![]));
        changes.last_mut().unwrap()
    }
}
pub fn update_area(
    area: &mut Area,
    conn: &SqliteConnection,
    mut record: &mut TranslationRecord,
) -> Result<()> {
    info!("Updating area {} (id {}).", area.name, area.osm_id);
    area.state = AreaState::GettingChanges;
    area.save(conn)?;
    let after = if let Some(timestamp) = &area.newest_osm_object_timestamp {
        info!(
            "Looking differences after the latest known OSM object timestamp {}",
            timestamp
        );
        DateTime::parse_from_rfc3339(timestamp)?.with_timezone(&Utc)
    } else {
        info!(
            "Looking differences after the area update time of {}",
            area.updated_at
        );
        DateTime::from_utc(area.updated_at, Utc)
    };
    let manager = OSMObjectManager::new();
    let mut area_db = AreaDatabase::open_existing(area.osm_id, true)?;
    let mut first = true;
    let mut osm_change_count = 0;
    let mut semantic_changes = vec![];
    let mut seen_unique_ids = HashSet::new();
    area_db.begin()?;
    for change in manager.lookup_differences_in(area.osm_id, &after)? {
        osm_change_count += 1;
        use OSMObjectChangeType::*;
        if first {
            area.state = AreaState::ApplyingChanges;
            area.save(conn)?;
            first = false;
        }
        let change = change?;
        if change.new.is_some()
            && (area.newest_osm_object_timestamp.is_none()
                || change.new.as_ref().unwrap().timestamp
                    > *area.newest_osm_object_timestamp.as_ref().unwrap())
        {
            area.newest_osm_object_timestamp = Some(change.new.as_ref().unwrap().timestamp.clone());
        }
        trace!("Processing OSM change {:?}", change);
        let id = change
            .old
            .as_ref()
            .unwrap_or_else(|| change.new.as_ref().expect("No old or new"))
            .unique_id();
        if seen_unique_ids.contains(&id) {
            warn!(
                "Phantom change of object with id {}, refusing to process change {:?}.",
                id, change
            );
            continue;
        } else {
            seen_unique_ids.insert(id);
        }
        let semantic_change = match change.change_type {
            Create => {
                let new = change.new.expect("No new for a create change");
                let mut cache = manager.get_cache();
                manager.cache_object_into(&mut cache, &new);
                drop(cache); // So we don't end up in a locked state for the cache db
                translator::translate(&new, &manager, &mut record)?
            }
            .map(|(o, ids)| {
                SemanticChange::creating(
                    o.id.to_string(),
                    o.geometry,
                    o.discriminator.to_string(),
                    o.data,
                    o.effective_width,
                    ids.map(|id| {
                        RootedEntityRelationship::new(&id, EntityRelationshipKind::OSMChild)
                    })
                    .collect(),
                )
            }),
            Delete => {
                let osm_id = change.old.expect("No old in a deletion change").unique_id();
                manager
                    .get_cache()
                    .remove::<Vec<u8>>(&osm_id.as_str())
                    .expect("Could not remove cached entity");
                if area_db.has_entity(&osm_id)? {
                    Some(SemanticChange::removing(&osm_id))
                } else {
                    None
                }
            }
            Modify => {
                let mut cache = manager.get_cache();
                let new_object = change.new.expect("No new during a modify");
                manager.cache_object_into(&mut cache, &new_object);
                drop(cache);
                let osm_id = new_object.unique_id();
                let old = area_db.get_entity(&osm_id)?;
                let new = translator::translate(&new_object, &manager, &mut record)?;
                match (old, new) {
                    (None, None) => None,
                    (Some(_), None) => Some(SemanticChange::removing(&osm_id)),
                    (None, Some((new, new_ids))) => Some(SemanticChange::creating(
                        new.id.to_string(),
                        new.geometry,
                        new.discriminator.to_string(),
                        new.data,
                        new.effective_width,
                        new_ids
                            .map(|id| {
                                RootedEntityRelationship::new(&id, EntityRelationshipKind::OSMChild)
                            })
                            .collect(),
                    )),
                    (Some(old), Some((new, new_ids))) => {
                        let (data_changes, property_changes) =
                            diff_utils::diff_entities(&old, &new)?;
                        let old_ids = area_db.get_entity_child_ids(&old.id)?;
                        let old_relationships: Vec<RootedEntityRelationship> = old_ids
                            .iter()
                            .map(|id| {
                                RootedEntityRelationship::new(id, EntityRelationshipKind::OSMChild)
                            })
                            .collect();
                        let new_relationships: Vec<RootedEntityRelationship> = new_ids
                            .map(|id| {
                                RootedEntityRelationship::new(&id, EntityRelationshipKind::OSMChild)
                            })
                            .collect();
                        let child_id_changes =
                            diff_utils::diff_lists(&old_relationships, &new_relationships)
                                .into_iter()
                                .map(|c| match c {
                                    ListChange::Add(v) => RelationshipChange::adding(v),
                                    ListChange::Remove(v) => RelationshipChange::removing(v),
                                })
                                .collect();
                        Some(SemanticChange::updating(
                            &osm_id,
                            property_changes,
                            data_changes,
                            child_id_changes,
                        ))
                    }
                }
            }
        };
        if let Some(semantic_change) = semantic_change {
            match area_db.apply_change(&semantic_change) {
                Ok(_) => semantic_changes.push(semantic_change),
                Err(e) => {
                    warn!(
                        "Failed to apply semantic change {:?} with error {}",
                        semantic_change, e
                    );
                }
            }
        }
    }
    area_db.apply_deferred_relationship_additions()?;
    info!(
        "Area updated successfully, applyed {} semantic changes resulting from {} OSM changes.",
        semantic_changes.len(),
        osm_change_count
    );
    info!("Inferring additional entity relationships and enriching the semantic changes...");
    //area_db.commit()?;
    //area_db.begin()?;
    infer_additional_relationships(&mut semantic_changes, &area_db)?;
    area_db.commit()?;
    let mut stream = ChangesStream::new_from_env(area.osm_id)?;
    if !stream.exists()? || !stream.should_publish_changes()? {
        info!("Not publishing the changes, because there is either no client to receive them, or all the clients have to redownload the area anyway.");
    } else {
        info!("Doing a garbage collection for the stream...");
        let prev_usage = stream.memory_usage()?;
        let collected = stream.garbage_collect()?;
        let current_usage = stream.memory_usage()?;
        info!("Garbage collection removed {} changes decreasing the memory usage of the stream from {} to {} bytes.", collected, prev_usage, current_usage);
        info!("Publishing the changes...");
        let mut batch = stream.begin_batch();
        for change in semantic_changes {
            batch.add_change(&change)?;
        }
        info!("Changes published and replies checked.");
    }
    let size = fs::metadata(AreaDatabase::path_for(area.osm_id, true))?.len() as i64;
    area.db_size = size;
    area.state = AreaState::Updated;
    area.save(conn)?;
    Ok(())
}

fn infer_additional_relationships(
    mut changes: &mut Vec<SemanticChange>,
    area_db: &AreaDatabase,
) -> Result<()> {
    let mut cache = HashMap::new();
    for idx in 0..changes.len() {
        if changes[idx].is_create() {
            let entity_id = changes[idx].osm_id().unwrap();
            debug!(
                "Enriching tags after creation resulting from {:?}, entity id {}.",
                changes[idx], entity_id
            );
            let mut entity = area_db
                .get_entity(entity_id)?
                .expect("Entity disappeared from a database");
            let relationships = relationship_inference::infer_additional_relationships_for_entity(
                &mut entity,
                area_db,
                &mut cache,
            )?;
            for relationship in relationships {
                let target = if relationship.parent_id == changes[idx].osm_id().unwrap() {
                    &mut changes[idx]
                } else {
                    find_or_create_suitable_change(&mut changes, &relationship.parent_id, false)
                };
                target.add_rooted_relationship(RootedEntityRelationship::new(
                    relationship.child_id.as_str(),
                    relationship.kind,
                ));
            }
        } else if changes[idx].is_update() {
            let entity_id = changes[idx].osm_id().unwrap();
            debug!(
                "Enriching relationships resulting from update {:?}, entity id {}.",
                changes[idx], entity_id
            );
            let current_relationships = area_db.get_relationships_related_to(entity_id)?;
            let mut entity = area_db.get_entity(entity_id)?.expect("Entity disappeared");
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
                let target = if parent_id == changes[idx].osm_id().unwrap() {
                    &mut changes[idx]
                } else {
                    find_or_create_suitable_change(&mut changes, &parent_id, true)
                };
                target.add_relationship_change(change);
            }
        }
    }
    Ok(())
}

pub fn update_area_databases() -> Result<()> {
    info!("Going to perform the area database update for all up-to date areas.");
    let area_db_conn = SqliteConnection::establish("server.db")?;
    let mut record = TranslationRecord::new();
    let areas = Area::all_updated(&area_db_conn)?;
    let now = Utc::now();
    for mut area in areas {
        update_area(&mut area, &area_db_conn, &mut record)?;
    }
    record.save_to_file(&format!("area_updates_{}.json", now.to_rfc3339()))?;
    info!("Area updates finished successfully.");
    Ok(())
}

#[derive(Serialize, Deserialize)]
pub struct UpdateAreaDatabasesTask;

#[typetag::serde]
impl doitlater::Executable for UpdateAreaDatabasesTask {
    fn execute(&self) -> std::result::Result<(), Box<dyn std::error::Error>> {
        update_area_databases().map_err(|e| Box::new(e) as Box<dyn std::error::Error>)
    }
}

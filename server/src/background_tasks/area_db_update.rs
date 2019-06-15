use crate::amqp_utils;
use crate::area::{Area, AreaState};
use crate::Result;
use crate::{area_messaging, diff_utils};
use chrono::{DateTime, Utc};
use diesel::{Connection, SqliteConnection};
use osm_api::change::OSMObjectChangeType;
use osm_api::object_manager::OSMObjectManager;
use osm_db::area_db::AreaDatabase;
use osm_db::semantic_change::SemanticChange;
use osm_db::translation::translator;
use tokio::await;
use std::thread;
use std::sync::mpsc;

enum UpdateMessage {
    ApplyChange(SemanticChange),
    Done
}

async fn update_area(mut area: Area) -> Result<()> {
    let area_name = area.name.clone();
    let (sender, receiver) = mpsc::channel();
    let handle = thread::spawn(move || -> Result<()> {
    info!("Updating area {}.", area.name);
    let conn = SqliteConnection::establish("server.db")?;
    area.state = AreaState::GettingChanges;
    area.save(&conn)?;
    let after = if let Some(timestamp) = &area.newest_osm_object_timestamp {
        info!(
            "Looking differences after the latest known OSM object timestamp {}",
            timestamp
        );
        DateTime::parse_from_rfc3339(&timestamp)?.with_timezone(&Utc)
    } else {
        info!(
            "Looking differences after the area update time of {}",
            area.updated_at
        );
        DateTime::from_utc(area.updated_at, Utc)
    };
    let manager = OSMObjectManager::new();
    let area_db = AreaDatabase::open_existing(&area.name)?;
    let mut first = true;
    let mut osm_change_count = 0;
    let mut semantic_change_count = 0;
    for change in manager.lookup_differences_in(&area.name, &after)? {
        osm_change_count += 1;
        use OSMObjectChangeType::*;
        if first {
            area.state = AreaState::ApplyingChanges;
            area.save(&conn)?;
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
        let semantic_change = match change.change_type {
            Create => translator::translate(
                &change.new.expect("No new object for a create change"),
                &manager,
            )?
            .map(|o| {
                SemanticChange::creating(o.geometry, o.discriminator, o.data, o.effective_width)
            }),
            Delete => {
                let osm_id = change.old.expect("No old in a deletion change").unique_id();
                if area_db.has_entity(&osm_id)? {
                    Some(SemanticChange::removing(&osm_id))
                } else {
                    None
                }
            }
            Modify => {
                let osm_id = change
                    .old
                    .as_ref()
                    .unwrap_or(change.new.as_ref().expect("No old or new"))
                    .unique_id();
                let old = area_db.get_entity(&osm_id)?;
                let new = translator::translate(
                    &change.new.expect("No new entity during a modify"),
                    &manager,
                )?;
                match (old, new) {
                    (None, None) => None,
                    (Some(_), None) => Some(SemanticChange::removing(&osm_id)),
                    (None, Some(new)) => Some(SemanticChange::creating(
                        new.geometry,
                        new.discriminator,
                        new.data,
                        new.effective_width,
                    )),
                    (Some(old), Some(new)) => {
                        let (data_changes, property_changes) =
                            diff_utils::diff_entities(&old, &new)?;
                        Some(SemanticChange::updating(
                            &osm_id,
                            property_changes,
                            data_changes,
                        ))
                    }
                }
            }
        };
        if let Some(semantic_change) = semantic_change {
            area_db.apply_change(&semantic_change)?;
            semantic_change_count += 1;
            sender.send(UpdateMessage::ApplyChange(semantic_change)).unwrap();
        }
    }
    area.state = AreaState::Updated;
    area.save(&conn)?;
    info!(
        "Area updated successfully, applyed {} semantic changes resulting from {} OSM changes.",
        semantic_change_count, osm_change_count
    );
        sender.send(UpdateMessage::Done).unwrap();
        Ok(())
    });
    let client = await!(amqp_utils::connect_to_broker())?;
    let mut channel = await!(client.create_channel())?;
        let mut semantic_changes = vec![];
        loop {
        match receiver.recv() {
            Ok(UpdateMessage::ApplyChange(change)) => semantic_changes.push(change),
        Ok(UpdateMessage::Done) => break,
        Err(e) => {
            let ret = handle.join().unwrap();
            warn!("Received error during recv call: {}", e);
            return ret;
        }
        }
    }
        info!("Publishing the changes...");
    for change in semantic_changes {
        await!(area_messaging::publish_change_on(&mut channel, change, area_name.clone()))?;
    }
    info!("Changes successfully published.");
    await!(channel.close(0, "Normal shutdown"))?;
    Ok(())
}

pub async fn update_area_databases() -> Result<()> {
    info!("Going to perform the area database update for all up-to date areas.");
    let areas = {
        let area_db_conn = SqliteConnection::establish("server.db")?;
        Area::all_updated(&area_db_conn)?
    };
    for area in areas {
        await!(update_area(area))?;
    }
    info!("Area updates finished successfully.");
    Ok(())
}

use crate::amqp_utils;
use crate::area::{Area, AreaState};
use crate::Result;
use crate::{area_messaging, diff_utils};
use chrono::{DateTime, Utc};
use diesel::{Connection, SqliteConnection};
use lapin::Channel;
use lapin::options::ConfirmSelectOptions;
use osm_api::change::OSMObjectChangeType;
use osm_api::object_manager::OSMObjectManager;
use osm_db::area_db::AreaDatabase;
use osm_db::semantic_change::SemanticChange;
use osm_db::translation::translator;

fn update_area(area: &mut Area, conn: &SqliteConnection, publish_channel: &Channel) -> Result<()> {
    info!("Updating area {} (id {}).", area.name, area.osm_id);
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
    let area_db = AreaDatabase::open_existing(area.osm_id, true)?;
    let mut first = true;
    let mut osm_change_count = 0;
    let mut semantic_changes = vec![];
    for change in manager.lookup_differences_in(area.osm_id, &after)? {
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
                    .unwrap_or_else(|| change.new.as_ref().expect("No old or new"))
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
            match area_db.apply_change(&semantic_change) {
                Ok(()) => {
                    semantic_changes.push(semantic_change);
                }
                Err(e) => error!("Failed to apply change {:?}, error: {}", semantic_change, e),
            }
        }
    }
    info!(
        "Area updated successfully, applyed {} semantic changes resulting from {} OSM changes.",
        semantic_changes.len(),
        osm_change_count
    );
    info!("Publishing the changes...");
    for change in semantic_changes {
        area_messaging::publish_change_on(&publish_channel, &change, area.osm_id)?;
    for confirmation in publish_channel.wait_for_confirms().wait()? {
        if confirmation.reply_code != 200 {
            warn!("Non 200 reply code from delivery: {:?}, code: {}, message: {}", confirmation.delivery, confirmation.reply_code, confirmation.reply_text);
        }
    }
    info!("One message done");
    }
    for confirmation in publish_channel.wait_for_confirms().wait()? {
        if confirmation.reply_code != 200 {
            warn!("Non 200 reply code from delivery: {:?}, code: {}, message: {}", confirmation.delivery, confirmation.reply_code, confirmation.reply_text);
        }
    }
    info!("Changes published and replies checked.");
    info!("After publishing, the channel status is: {:?}", publish_channel.status());
    area.state = AreaState::Updated;
    area.save(&conn)?;
    Ok(())
}

pub fn update_area_databases() -> Result<()> {
    info!("Going to perform the area database update for all up-to date areas.");
    let area_db_conn = SqliteConnection::establish("server.db")?;
    let areas = Area::all_updated(&area_db_conn)?;
    let rabbitmq_conn = amqp_utils::connect_to_broker()?;
    let channel = rabbitmq_conn.create_channel().wait()?;
    channel.confirm_select(ConfirmSelectOptions::default()).wait()?;
    for mut area in areas {
        update_area(&mut area, &area_db_conn, &channel)?;
    }
    info!("Area updates finished successfully.");
    info!("Before closing, the channel status is: {:?}", channel.status());
    info!("Before closing, the connection status is: {:?}", rabbitmq_conn.status());
    channel.close(200, "Normal shutdown").wait()?;
    info!("AMQP channel closed.");
    rabbitmq_conn.close(200, "Normal shutdown").wait()?;
    info!("Connection closed.");
    Ok(())
}

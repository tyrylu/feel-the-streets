use crate::area::Area;
use crate::db;
use osm_api::replication::{OSMChange, OSMChanges};
use rusqlite::Connection;
use std::collections::{HashMap, HashSet};

pub(crate) fn filter_and_deduplicate_changes(
    changes: OSMChanges,
    conn: &Connection,
) -> Vec<OSMChange> {
    let mut filtered = Vec::with_capacity(changes.0.len());
    let mut seen_ids = HashSet::new();
    let mut interests = HashMap::new();
    for change in changes.0.into_iter().rev() {
        // We are not storing admin_level 2 entities
        if change.object().tags.get("admin_level") == Some(&"2".to_string()) {
            continue;
        }
        // We're also ignoring changes for the North Atlantic Treaty Organization, we will not store its geometry either.
        if change.object().tags.get("name:en") == Some(&"North Atlantic Treaty Organization".to_string()) {
            continue;
        }
        if !changeset_might_be_interesting(change.changeset(), &mut interests, conn) {
            continue;
        }
        match change {
            OSMChange::Create(o) if seen_ids.contains(&o.unique_id()) => continue, // We already saw an update, or a delete change, so we already have the newest picture of the change.
            c @ OSMChange::Create(_) => {
                seen_ids.insert(c.object_unique_id());
                filtered.push(c);
            }
            OSMChange::Modify(o) if seen_ids.contains(&o.unique_id()) => continue, // We saw a newer update or delete already, so this one is redundant.
            c @ OSMChange::Modify(_) => {
                seen_ids.insert(c.object_unique_id());
                filtered.push(c);
            }
            c @ OSMChange::Delete(_) => {
                seen_ids.insert(c.object_unique_id());
                filtered.push(c)
            }
        }
    }
    filtered.reverse();
    filtered
}

fn changeset_might_be_interesting(
    changeset: u64,
    changeset_interests: &mut HashMap<u64, bool>,
    conn: &Connection,
) -> bool {
    *changeset_interests.entry(changeset).or_insert_with(|| {
        debug!("Getting information about changeset {}", changeset);
        if let Some(changeset) = db::get_changeset(conn, changeset)
            .expect("Could not get changeset info") {
        !Area::all_containing(conn, &changeset.bounds.as_wkb_polygon())
            .expect("Could not get areas containing the given bounds")
               .is_empty()
            }
        else {
            warn!("Did not find changeset {} or it had no bounds, assuming it might be interesting.", changeset);
            true
    }
})
}
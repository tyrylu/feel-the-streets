use crate::area::Area;
use osm_api::main_api::MainAPIClient;
use osm_api::replication::{OSMChange, OSMChanges};
use rusqlite::Connection;
use std::collections::{HashMap, HashSet};

pub(crate) fn filter_and_deduplicate_changes(
    changes: OSMChanges,
    m_api: &MainAPIClient,
    conn: &Connection,
) -> Vec<OSMChange> {
    let mut filtered = Vec::with_capacity(changes.0.len());
    let mut seen_ids = HashSet::new();
    let mut interests = HashMap::new();
    for change in changes.0.into_iter().rev() {
        if !changeset_might_be_interesting(change.changeset(), &mut interests, m_api, conn) {
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

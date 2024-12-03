use osm_api::SmolStr;
use osm_db::semantic_change::SemanticChange;
use std::collections::{HashMap, HashSet};

#[derive(Default)]
pub(crate) struct AreaInfo<'a> {
    pub changes: Vec<SemanticChange>,
    pub geometry: Option<Vec<u8>>,
    pub newest_timestamp: &'a str,
}

#[derive(Default)]
pub(crate) struct SemanticChangesContainer<'a> {
    changes: HashMap<i64, AreaInfo<'a>>,
    needs_geometry_update: HashSet<SmolStr>,
    seen_entity_ids: HashSet<SmolStr>,
}

impl<'a> SemanticChangesContainer<'a> {
    pub fn add_change(&mut self, area: i64, change: SemanticChange) {
        self.seen_entity_ids.insert(change.osm_id().into());
        self.changes.entry(area).or_default().changes.push(change);
    }

    pub fn iter_mut(&mut self) -> impl Iterator<Item = (&i64, &mut AreaInfo<'a>)> {
        self.changes.iter_mut()
    }

    pub fn update_geometry_for(&mut self, area_id: i64, geometry: Vec<u8>) {
        self.changes.entry(area_id).or_default().geometry = Some(geometry);
    }

    pub fn update_newest_timestamp_for(&mut self, area_id: i64, timestamp: &'a str) {
        let entry = self.changes.entry(area_id).or_default();
        if entry.newest_timestamp < timestamp {
            entry.newest_timestamp = timestamp;
        }
    }

    pub fn record_geometry_update_requirement(&mut self, entity_id: &str) {
        self.needs_geometry_update.insert(entity_id.into());
    }

    pub fn entities_needing_geometry_update(&self) -> HashSet<SmolStr> {
        self.needs_geometry_update
            .difference(&self.seen_entity_ids)
            .cloned()
            .collect()
    }
}

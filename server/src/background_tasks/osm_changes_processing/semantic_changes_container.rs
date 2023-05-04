use osm_db::semantic_change::SemanticChange;
use std::collections::HashMap;

#[derive(Default)]
pub(crate) struct AreaInfo<'a> {
    pub changes: Vec<SemanticChange>,
    pub geometry: Option<Vec<u8>>,
    pub newest_timestamp: &'a str
}

#[derive(Default)]
pub(crate) struct SemanticChangesContainer<'a>(HashMap<i64, AreaInfo<'a>>);

impl<'a> SemanticChangesContainer<'a> {
    pub fn add_change(&mut self, area: i64, change: SemanticChange) {
        self.0.entry(area).or_default().changes.push(change);
    }

    pub fn iter_mut(&mut self) -> impl Iterator<Item=(&i64, &mut AreaInfo<'a>)> {
        self.0.iter_mut()
    }

    pub fn update_geometry_for(&mut self, area_id: i64, geometry: Vec<u8>) {
        self.0.entry(area_id).or_default().geometry = Some(geometry);
    }

    pub fn update_newest_timestamp_for(&mut self, area_id: i64, timestamp: &'a str) {
        let entry = self.0.entry(area_id).or_default();
        if entry.newest_timestamp < timestamp {
            entry.newest_timestamp = timestamp;
        }
    }
    }
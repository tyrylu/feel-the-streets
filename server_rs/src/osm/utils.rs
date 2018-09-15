use itertools::Itertools;
use osm::object::OSMObject;
use serde_json;
use std::collections::HashMap;

const POLYGON_CRITERIA_STR: &str = include_str!("polygon_criteria.json");
lazy_static! {
    static ref POLYGON_CRITERIA: Vec<PolygonCreationCriterion> =
        { serde_json::from_str::<Vec<PolygonCreationCriterion>>(&POLYGON_CRITERIA_STR).unwrap() };
}

#[derive(Deserialize)]
struct PolygonCreationCriterion {
    key: String,
    polygon: String,
    #[serde(default)]
    values: Vec<String>,
}

pub fn object_should_have_closed_geometry(object: &OSMObject) -> bool {
    for criterion in POLYGON_CRITERIA.iter() {
        if object.tags.contains_key(&criterion.key) {
            let should = match criterion.polygon.as_str() {
                "all" => true,
                "whitelist" => criterion.values.contains(&object.tags[&criterion.key]),
                "blacklist" => !criterion.values.contains(&object.tags[&criterion.key]),
                _ => unreachable!(),
            };
            return should;
        }
    }
    false
}

pub fn ensure_closed(coords: &mut Vec<(f64, f64)>) {
    if coords.first().unwrap() != coords.last().unwrap() {
                let new_last = coords.first().unwrap().clone();
                coords.push(new_last);
    }
}

pub fn coords_to_text(coords: &Vec<(f64, f64)>) -> String {
    coords
        .iter()
        .map(|coord| format!("{}, {}", coord.0, coord.1))
        .join(", ")
}

fn find_connectable_segments(segments: Vec<Vec<(f64, f64)>>) -> (Option<Vec<(f64, f64)>>, Option<Vec<(f64, f64)>>) {
    if segments.len() == 1 {
        return (None, None);
    }
    let mut starts = HashMap::new();
    let mut ends = HashMap::new();
    for segment in segments {
        starts.insert(segment[0], segment);
        ends.insert(segment[segment.len() - 1], segment);
    }
    for end in ends.keys() {
        if starts.contains_key(end) {
            return (ends[end], starts[end]);
        }
    }
    return (None, None);
    }

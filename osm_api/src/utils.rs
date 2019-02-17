use crate::object::OSMObject;
use itertools::Itertools;
use serde_json;
use std::collections::HashMap;

type Segment = Vec<(f64, f64)>;
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
        let new_last = *coords.first().unwrap();
        coords.push(new_last);
    }
}

pub fn coords_to_text(coords: &[(f64, f64)]) -> String {
    coords
        .iter()
        .map(|coord| format!("{} {}", coord.0, coord.1))
        .join(", ")
}

fn find_connectable_segments<'a>(
    segments: &'a [Segment],
) -> (Option<&'a Segment>, Option<&'a Segment>) {
    if segments.len() == 1 {
        return (None, None);
    }
    let mut starts = HashMap::new();
    let mut ends = HashMap::new();
    for segment in segments {
        starts.insert((segment[0].0.to_bits(), segment[0].1.to_bits()), segment);
        ends.insert(
            (
                segment[segment.len() - 1].0.to_bits(),
                segment[segment.len() - 1].1.to_bits(),
            ),
            segment,
        );
    }
    for end in ends.keys() {
        if starts.contains_key(end) {
            return (Some(ends[end]), Some(starts[end]));
        }
    }
    (None, None)
}

pub fn connect_polygon_segments(segments: &mut Vec<Segment>) {
    loop {
        let cloned_segments = segments.clone();
        let (mut first, second) = find_connectable_segments(&cloned_segments);
        if first.is_none() {
            break;
        }
        let second_unwrapped = second.unwrap();
        let mut first_unwrapped = first.as_mut().unwrap().clone();
        segments.retain(|s| s != second_unwrapped);
        first_unwrapped.extend_from_slice(&second_unwrapped[1..]);
    }
    for mut segment in segments.iter_mut() {
        ensure_closed(&mut segment);
    }
}

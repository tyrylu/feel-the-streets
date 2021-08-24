use crate::object::OSMObject;
use geo_types::LineString;
use std::collections::HashMap;
use once_cell::sync::Lazy;

const POLYGON_CRITERIA_STR: &str = include_str!("polygon_criteria.json");
    static POLYGON_CRITERIA: Lazy<Vec<PolygonCreationCriterion>> =
        Lazy::new(|| {serde_json::from_str::<Vec<PolygonCreationCriterion>>(POLYGON_CRITERIA_STR).unwrap()});

#[derive(serde::Deserialize)]
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

pub fn ensure_closed(coords: &mut LineString<f64>) {
    if coords.0.first().unwrap() != coords.0.last().unwrap() {
        let new_last = *coords.0.first().unwrap();
        coords.0.push(new_last);
    }
}

fn find_connectable_segments(
    segments: &[LineString<f64>],
) -> (Option<&LineString<f64>>, Option<&LineString<f64>>) {
    if segments.len() == 1 {
        return (None, None);
    }
    let mut starts = HashMap::new();
    let mut ends = HashMap::new();
    for segment in segments {
        starts.insert((segment.0[0].x.to_bits(), segment[0].y.to_bits()), segment);
        ends.insert(
            (
                segment.0[segment.0.len() - 1].x.to_bits(),
                segment.0[segment.0.len() - 1].y.to_bits(),
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

pub fn connect_polygon_segments(segments: &mut Vec<LineString<f64>>) {
    loop {
        let cloned_segments = segments.clone();
        let (mut first, second) = find_connectable_segments(&cloned_segments);
        if first.is_none() {
            break;
        }
        let second_unwrapped = second.unwrap();
        let mut first_unwrapped = first.as_mut().unwrap().clone();
        segments.retain(|s| s != second_unwrapped);
        first_unwrapped
            .0
            .extend_from_slice(&second_unwrapped.0[1..]);
    }
    for mut segment in segments.iter_mut() {
        ensure_closed(&mut segment);
    }
}

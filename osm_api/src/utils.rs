use crate::object::OSMObject;
use geo_types::{Coord, Geometry, LineString};
use once_cell::sync::Lazy;
use std::collections::HashMap;

const POLYGON_CRITERIA_STR: &str = include_str!("polygon_criteria.json");
static POLYGON_CRITERIA: Lazy<Vec<PolygonCreationCriterion>> = Lazy::new(|| {
    serde_json::from_str::<Vec<PolygonCreationCriterion>>(POLYGON_CRITERIA_STR).unwrap()
});

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

fn coord_to_key(coord: Coord<f64>) -> ([u8; 8], [u8; 8]) {
    (coord.x.to_le_bytes(), coord.y.to_le_bytes())
}

fn merge_to_from_end(merge_to: &mut LineString<f64>, mut merge_from: LineString<f64>) {
    let last_coord_idx = merge_from.0.len() - 1;
    if merge_from[last_coord_idx] == merge_to[0] {
        // We have the merge_to coords, and then the merge_from ones, except for the last one.
        merge_to
            .0
            .splice(0..0, merge_from.0[0..last_coord_idx].iter().copied());
    } else {
        // We have the coords in merge_to, and then the ones from merge_from, except the last one, but reversed, because we need to preserve the line.
        merge_from.0.reverse();
        merge_to.0.extend_from_slice(&merge_from.0[1..]);
    }
}

fn merge_to_from_start(merge_to: &mut LineString<f64>, merge_from: LineString<f64>) {
    if merge_from[0] == merge_to[0] {
        // We have the reversed merge_to coords, and then the ones from merge_from, except for the first.
        merge_to.0.reverse();
    }
    // Now, we definitely have the coordinate match as the last coord of merge_to and first coord of merge_from, so both cases are now the same.
    merge_to.0.extend_from_slice(&merge_from.0[1..]);
}

pub fn connect_polygon_segments(segments: &mut Vec<LineString<f64>>) {
    let mut did_connect_segments = true;
    while did_connect_segments {
        did_connect_segments = false;
        let mut end_points = HashMap::new();
        let mut current_segment_idx = 0;
        while current_segment_idx < segments.len() {
            let current_segment = &mut segments[current_segment_idx];
            if let Some(previous_segment_idx) = end_points.get(&coord_to_key(current_segment[0])) {
                let removed_segment = segments.swap_remove(current_segment_idx);
                merge_to_from_start(&mut segments[*previous_segment_idx], removed_segment);
                did_connect_segments = true;
            } else if let Some(previous_segment_idx) =
                end_points.get(&coord_to_key(current_segment[current_segment.0.len() - 1]))
            {
                let removed_segment = segments.swap_remove(current_segment_idx);
                merge_to_from_end(&mut segments[*previous_segment_idx], removed_segment);
                did_connect_segments = true;
            } else {
                end_points.insert(coord_to_key(current_segment[0]), current_segment_idx);
                end_points.insert(
                    coord_to_key(current_segment[current_segment.0.len() - 1]),
                    current_segment_idx,
                );
                current_segment_idx += 1;
            }
        }
    }
    for segment in segments.iter_mut() {
        segment.close();
    }
}

fn unnest_geometry_to_parts(geom: Geometry<f64>) -> Vec<Geometry<f64>> {
    let mut parts = vec![];
    match geom {
        Geometry::Point(p) => parts.push(p.into()),
        Geometry::Polygon(p) => parts.push(p.into()),
        Geometry::LineString(l) => parts.push(l.into()),
        Geometry::MultiLineString(ml) => {
            parts.append(&mut ml.0.into_iter().map(|p| p.into()).collect())
        }
        Geometry::MultiPoint(mp) => parts.append(&mut mp.0.into_iter().map(|p| p.into()).collect()),
        Geometry::MultiPolygon(mp) => {
            parts.append(&mut mp.0.into_iter().map(|p| p.into()).collect())
        }
        Geometry::GeometryCollection(gc) => {
            parts.extend(gc.iter().flat_map(|g| unnest_geometry_to_parts(g.clone())))
        }
        g => panic!("Geometry {g:?} not supported yet."),
    }
    parts
}

pub(crate) fn unnest_geometry(geom: Geometry<f64>) -> Geometry<f64> {
    let mut parts = unnest_geometry_to_parts(geom);
    if parts.len() == 1 {
        parts.pop().unwrap()
    } else {
        Geometry::GeometryCollection(parts.into())
    }
}

pub fn unnest_wkb_geometry(mut geom: &[u8]) -> Vec<u8> {
    let parsed = wkb::wkb_to_geom(&mut geom).expect("Unnest, could not parse geometry");
    wkb::geom_to_wkb(&unnest_geometry(parsed)).expect("Unnest, could not write geometry")
}

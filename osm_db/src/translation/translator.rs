use super::checks;
use super::conversions;
use super::spec::TranslationSpec;
use crate::entity::NotStoredEntity;
use osm_api::error::*;
use osm_api::object::OSMObject;
use osm_api::object_manager::OSMObjectManager;
use std::collections::HashMap;

pub fn translate(
    object: &OSMObject,
    manager: &OSMObjectManager,
) -> Result<Option<NotStoredEntity>> {
    let lookup_res = TranslationSpec::for_object(&object);
    match lookup_res {
        None => Ok(None),
        Some((discriminator, spec)) => {
            let mut entity_data = HashMap::new();
            trace!(
                "Translating object {} to {}.",
                object.unique_id(),
                discriminator
            );
            for (key, value) in &object.tags {
                let mut new_key = key.clone();
                let mut new_value = value.clone();
                if spec.renames.contains_key(key) {
                    new_key = spec.renames[key].clone();
                }
                let prefix = format!("{}:", key);
                if spec.unprefixes.contains(key) {
                    new_key = new_key.replace(&prefix, "");
                }
                if spec.replaces_property_value.contains_key(key) {
                    let replacements = &spec.replaces_property_value[key];
                    for (old, new) in replacements.iter() {
                        new_value = new_value.replace(old, new);
                    }
                }
                entity_data.insert(new_key, new_value);
            }
            let converted_data = conversions::convert_entity_data(&discriminator, &entity_data);
            if !checks::check_entity_data_consistency(&discriminator, &converted_data) {
                return Ok(None);
            }
            let raw_data =
                serde_json::to_string(&converted_data).expect("Could not serialize entity data.");
            let geometry = manager.get_geometry_as_wkt(&object)?;
            match geometry {
                Some(geom) => {
                    let effective_width = calculate_effective_width(&discriminator, &entity_data);
                    Ok(Some(NotStoredEntity {
                        discriminator,
                        effective_width,
                        geometry: geom,
                        data: raw_data,
                    }))
                }
                None => {
                    warn!("Failed to generate geometry for object {:?}", &object);
                    Ok(None)
                }
            }
        }
    }
}
fn calculate_effective_width(discriminator: &str, tags: &HashMap<String, String>) -> Option<f64> {
    match discriminator {
        "PowerLine" => Some(f64::from(0)),
        "WaterWay" => Some(
            tags.get("width")
                .unwrap_or(&"0".to_string())
                .parse()
                .expect("Could not parse width as f64"),
        ),
        "Road" => {
            if tags.contains_key("width") {
                Some(
                    tags["width"]
                        .parse()
                        .expect("Could not parse width as f64."),
                )
            } else if tags.contains_key("est_width") {
                Some(
                    tags["est_width"]
                        .parse()
                        .expect("Could not parse width as f64."),
                )
            } else if tags.contains_key("carriageway_width") {
                Some(
                    tags["carriageway_width"]
                        .parse()
                        .expect("Could not parse width as f64."),
                )
            } else {
                let lanes: u32 = tags
                    .get("lanes")
                    .unwrap_or(&"0".to_string())
                    .parse()
                    .expect("Could not parse lane count.");
                let width: u32 = tags
                    .get("lanes_maxwidth")
                    .unwrap_or(&"2".to_string())
                    .parse()
                    .expect("Failed to parse lanes_maxwidth");
                Some(f64::from(lanes * width))
            }
        }
        _ => None,
    }
}

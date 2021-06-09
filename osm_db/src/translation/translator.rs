use super::checks;
use super::conversions;
use super::record::TranslationRecord;
use super::spec::TranslationSpec;
use crate::entity::Entity;
use crate::Error;
use hashbrown::HashMap;
use osm_api::object::OSMObject;
use osm_api::object_manager::OSMObjectManager;
use osm_api::SmolStr;
use serde_json::Value;

pub fn translate(
    object: &OSMObject,
    manager: &OSMObjectManager,
    mut record: &mut TranslationRecord,
) -> Result<Option<(Entity, Box<dyn Iterator<Item = String>>)>, Error> {
    let lookup_res = TranslationSpec::primary_discriminator_for_object(object);
    match lookup_res {
        None => {
            let mut interesting_len = object.tags.len();
            if object.tags.contains_key("created_by") {
                interesting_len -= 1;
            }
            if object.tags.contains_key("source") {
                interesting_len -= 1;
            }
            if interesting_len > 0 {
                record.add_potentially_interesting_object(object.clone());
            } else {
                trace!(
                    "Did not find a translation spec for object {}.",
                    object.unique_id()
                );
            }
            Ok(None)
        }
        Some(discriminator) => {
            let mut entity_data = HashMap::new();
            trace!(
                "Translating object {} to {}.",
                object.unique_id(),
                discriminator
            );
            let specs = TranslationSpec::all_relevant_for(&discriminator);
            for (key, value) in &object.tags {
                let mut new_key = key.clone();
                let mut new_value = value.clone();
                for spec in &specs {
                    if spec.renames.contains_key(key) {
                        new_key = spec.renames[key].clone();
                        break;
                    }
                    for unprefixes in &spec.unprefixes {
                        if new_key.starts_with(unprefixes) {
                            trace!("Unprefixing {}.", new_key);
                            new_key = new_key.replace(&format!("{}:", unprefixes), "");
                            break;
                        }
                    }
                    if spec.replaces_property_value.contains_key(key) {
                        let replacements = &spec.replaces_property_value[key];
                        for (old, new) in replacements.iter() {
                            new_value = new_value.replace(old, new);
                        }
                    }
                }
                entity_data.insert(new_key, new_value);
            }
            // Common fields
            entity_data.insert("timestamp".to_string(), object.timestamp.clone());
            entity_data.insert("version".to_string(), object.version.to_string());
            entity_data.insert("changeset".to_string(), object.changeset.to_string());
            entity_data.insert("user".to_string(), object.user.clone());
            entity_data.insert("uid".to_string(), object.uid.to_string());
            let mut converted_data =
                conversions::convert_entity_data(&discriminator, &entity_data, &mut record);
            // Address, must be done there, because we need to nest the object.
            let mut aware = false;
            for spec in &specs {
                aware |= spec.address_aware.unwrap_or(false);
            }
            if aware {
                let (address_data, address_field_names) =
                    conversions::convert_address(&object.tags);
                if !address_data.is_empty() {
                    let mut new_data = serde_json::Map::new();
                    for (k, v) in address_data.iter() {
                        new_data.insert(k.clone(), Value::from(v.clone()));
                    }
                    converted_data.insert("address".to_string(), Value::from(new_data));
                    // Now, remove the original addr parts
                    for field_name in address_field_names {
                        converted_data.remove(field_name);
                    }
                }
            }

            if !checks::check_entity_data_consistency(&discriminator, &converted_data, &mut record)
            {
                return Ok(None);
            }
            let raw_data =
                serde_json::to_string(&converted_data).expect("Could not serialize entity data.");
            let geometry = manager.get_geometry_as_wkb(object)?;
            match geometry {
                Some(geom) => {
                    let effective_width = calculate_effective_width(&discriminator, &entity_data);
                    Ok(Some((
                        Entity {
                            id: object.unique_id(),
                            discriminator: SmolStr::new_inline(&discriminator),
                            effective_width,
                            geometry: geom,
                            data: raw_data,
                            parsed_data: None,
                        },
                        Box::new(object.related_ids().map(|(id, _)| id)),
                    )))
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
        "WaterWay" => match tags.get("width").map(|w| w.as_str()).unwrap_or("0").parse() {
            Ok(val) => Some(val),
            Err(e) => {
                warn!(
                    "Could not parse with during an effective width calculation: {}",
                    e
                );
                None
            }
        },

        "Road" | "ServiceRoad" | "Track" => {
            if tags.contains_key("width") {
                match tags["width"].parse() {
                    Ok(val) => Some(val),
                    Err(e) => {
                        warn!(
                            "Could not parse width for the effective width calcullation, error: {}",
                            e
                        );
                        None
                    }
                }
            } else if tags.contains_key("est_width") {
                match tags["est_width"].parse() {
                    Ok(val) => Some(val),
                    Err(e) => {
                        warn!("Could not parse est_width during effective width calculation, error: {}", e);
                        None
                    }
                }
            } else if tags.contains_key("carriageway_width") {
                match tags["carriageway_width"].parse() {
                    Ok(val) => Some(val),
                    Err(e) => {
                        warn!("Could not parse carriageway_width during effective width calculation, error: {}", e);
                        None
                    }
                }
            } else {
                let lanes: u32 = match tags.get("lanes").map(|l| l.as_str()).unwrap_or("2").parse()
                {
                    Ok(val) => val,
                    Err(e) => {
                        warn!("Failed to parse lane count, error: {}", e);
                        2
                    }
                };
                let width: u32 = match tags
                    .get("lanes_maxwidth")
                    .map(|l| l.as_str())
                    .unwrap_or("2")
                    .parse()
                {
                    Ok(val) => val,
                    Err(e) => {
                        warn!("Failed to parse lanes_maxwidth, error {}", e);
                        2
                    }
                };
                Some(f64::from(lanes * width))
            }
        }
        _ => None,
    }
}

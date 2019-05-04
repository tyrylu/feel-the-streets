use super::checks;
use super::conversions;
use super::spec::TranslationSpec;
use crate::entity::NotStoredEntity;
use osm_api::object::OSMObject;
use osm_api::object_manager::OSMObjectManager;
use hashbrown::HashMap;

pub fn translate(
    object: &OSMObject,
    manager: &OSMObjectManager,
) -> Result<Option<NotStoredEntity>, failure::Error> {
                            let lookup_res = TranslationSpec::for_object(&object);
    match lookup_res {
        None => {
            if object.tags.len() > 1 {
            warn!(
                "Did not find a translation spec for potentially interesting object {:?}.",
                object
            );
            }
            else {
                trace!(
                "Did not find a translation spec for object {}.",
                object.unique_id()
            );
                        }
            Ok(None)
        }
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
                for unprefixes in &spec.unprefixes {
                    if new_key.starts_with(unprefixes) {
                        trace!("Unprefixing {}.", new_key);
                        new_key = new_key.replace(&format!("{}:", unprefixes), "");
                    }
                }
                if spec.replaces_property_value.contains_key(key) {
                    let replacements = &spec.replaces_property_value[key];
                    for (old, new) in replacements.iter() {
                        new_value = new_value.replace(old, new);
                    }
                }
                entity_data.insert(new_key, new_value);
            }
            if let Some(aware) = spec.address_aware {
                if aware {
                let address_data = conversions::convert_address(&object.tags);
                if address_data.len() > 2 {
                entity_data.insert("address".to_string(), address_data);
                }
                }
            }
            // Common fields
            entity_data.insert("osm_id".to_string(), object.unique_id());
            entity_data.insert("timestamp".to_string(), object.timestamp.clone());
            entity_data.insert("version".to_string(), object.version.to_string());
            entity_data.insert("changeset".to_string(), object.changeset.to_string());
            entity_data.insert("user".to_string(), object.user.clone());
            entity_data.insert("uid".to_string(), object.uid.to_string());

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
        "WaterWay" => match tags.get("width").unwrap_or(&"0".to_string()).parse() {
            Ok(val) => Some(val),
            Err(e) => {
                warn!(
                    "Could not parse with during an effective width calculation: {}",
                    e
                );
                None
            }
        },

        "Road" => {
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
                let lanes: u32 = match tags.get("lanes").unwrap_or(&"2".to_string()).parse() {
                    Ok(val) => val,
                    Err(e) => {
                        warn!("Failed to parse lane count, error: {}", e);
                        2
                    }
                };
                let width: u32 = match tags
                    .get("lanes_maxwidth")
                    .unwrap_or(&"2".to_string())
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

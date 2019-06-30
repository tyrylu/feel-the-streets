use crate::semantic_change::EntryChange;
use serde_json::{Map, Value};

#[derive(Debug)]
pub struct NotStoredEntity {
    pub geometry: String,
    pub discriminator: String,
    pub data: String,
    pub effective_width: Option<f64>,
}

pub struct Entity {
    pub id: i32,
    pub geometry: String,
    pub discriminator: String,
    pub data: String,
    pub effective_width: Option<f64>,
}

impl Entity {
    pub fn apply_property_changes(&mut self, property_changes: &[EntryChange]) {
        for change in property_changes {
            if let EntryChange::Update { key, new_value, .. } = change {
                match key.as_ref() {
                    "geometry" => {
                        self.geometry = new_value
                            .as_str()
                            .expect("Non-string attempted to be set as a geometry")
                            .to_string()
                    }
                    "discriminator" => {
                        self.discriminator = new_value
                            .as_str()
                            .expect("Non-string attempted to be set as a discriminator")
                            .to_string()
                    }
                    "data" => {
                        self.data = new_value
                            .as_str()
                            .expect("Non-string attempted to be set as the data")
                            .to_string()
                    }
                    "effective_width" => {
                        if new_value.is_null() {
                            self.effective_width = None;
                        } else {
                            self.effective_width = Some(new_value.as_f64().expect("Something else than a f64 or a null attempted to be set as the effective width"));
                        }
                    }
                    _ => warn!(
                        "Unsupported key {} attempted to be set on this object.",
                        key
                    ),
                }
            } else {
                warn!("Unsupported entry change not applied: {:?}", change);
            }
        }
    }

    pub fn apply_data_changes(&mut self, changes: &[EntryChange]) {
        use EntryChange::*;
        let mut value: Value =
            serde_json::from_str(&self.data).expect("Could not deserialize data");
        if !value.is_object() {
            warn!("Entity data was not a map, it was instead: {}", value);
        } else {
            let mut data_map = value.as_object_mut().unwrap();
            for change in changes {
                match change {
                    Create { key, value } => {
                        let (target, final_key_part) =
                            get_target_of_key(&key, &mut data_map, true).unwrap();
                        target.insert(final_key_part, value.clone());
                    }
                    Remove { key } => {
                        if let Some((target, final_key_part)) =
                            get_target_of_key(&key, &mut data_map, false)
                        {
                            target.remove(&final_key_part);
                        } else {
                            warn!("Deletion of value at key {} not possible, one of the intermediary maps was not found.", key);
                        }
                    }
                    Update { key, new_value, .. } => {
                        if let Some((target, final_key_part)) =
                            get_target_of_key(&key, &mut data_map, false)
                        {
                            match target.get_mut(&final_key_part) {
                                Some(val) => *val = new_value.clone(),
                                None => {
                                    warn!("Final key {} was missing, not updated.", final_key_part)
                                }
                            }
                        } else {
                            warn!("Update of value at key {} not possible, one of the intermediary maps was not found.", key);
                        }
                    }
                }
            }
            self.data = serde_json::to_string(&data_map).expect("Failed to serialize data map.");
        }
    }
}

fn get_target_of_key<'a>(
    key: &str,
    map: &'a mut Map<String, Value>,
    create_if_missing: bool,
) -> Option<(&'a mut Map<String, Value>, String)> {
    let mut current_map = map;
    let mut subkeys_iter = key.split("/").peekable();
    let mut final_key_part = "should_not_happen";
    while let Some(subkey) = subkeys_iter.next() {
        if subkeys_iter.peek().is_some() {
            // It's a key leading to the target
            if current_map.contains_key(subkey) {
                let val = &mut current_map[&subkey.to_string()];
                if val.is_object() {
                    current_map = val.as_object_mut().unwrap();
                } else {
                    warn!(
                        "The subkey {} was found in the parent object, but it was not a map.",
                        &subkey
                    );
                    return None;
                }
            } else {
                if create_if_missing {
                    current_map.insert(subkey.to_string(), Value::Object(Map::new()));
                    current_map = current_map
                        .get_mut(subkey)
                        .unwrap()
                        .as_object_mut()
                        .unwrap();
                } else {
                    return None;
                }
            }
        } else {
            final_key_part = subkey;
        }
    }
    Some((current_map, final_key_part.to_string()))
}

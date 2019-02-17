use crate::Result;
use serde_json::{Map, Value};
use osm_db::entity::{Entity, NotStoredEntity};
use osm_db::semantic_change::EntryChange;
use std::collections::HashSet;

fn diff_properties(old: &Entity, new: &NotStoredEntity) -> Vec<EntryChange> {
    let mut changes = vec![];
    if old.geometry != new.geometry {
        changes.push(EntryChange::updating("geometry", Value::from(new.geometry.clone())));
    }
if old.discriminator != new.discriminator {
        changes.push(EntryChange::updating("discriminator", Value::from(new.discriminator.clone())));
    }
if old.effective_width != new.effective_width {
        changes.push(EntryChange::updating("effective_width", new.effective_width.map(|w| Value::from(w)).unwrap_or(Value::Null)));
    }
changes
}

fn diff_json_maps(old: &str, new: &str) -> Result<Vec<EntryChange>> {
    let old_map: Map<String, Value> = serde_json::from_str(&old)?;
    let new_map: Map<String, Value> = serde_json::from_str(&new)?;
Ok(diff_json_maps_internal(&old_map, &new_map, None))
}

fn diff_json_maps_internal(old: &Map<String, Value>, new: &Map<String, Value>, key_prefix: Option<String>) -> Vec<EntryChange> {
    let mut changes = vec![];
    let old_keys: HashSet<&String> = old.keys().collect();
    let new_keys: HashSet<&String> = new.keys().collect();
    let added = new_keys.difference(&old_keys);
    let removed = old_keys.difference(&new_keys);
    let stayed = old_keys.intersection(&new_keys);
    for added_key in added {
        changes.push(EntryChange::creating(&to_composite_key(&key_prefix, &added_key), new[*added_key].clone()));
    }
    for removed_key in removed {
        changes.push(EntryChange::removing(&to_composite_key(&key_prefix, &removed_key)));
    }
for stayed_key in stayed {
    let old_val = &old[*stayed_key];
    let new_val = &new[*stayed_key];
    if old_val != new_val {
        if old_val.is_object() && new_val.is_object() {
            changes.extend(diff_json_maps_internal(&old_val.as_object().unwrap(), &new_val.as_object().unwrap(), Some(to_composite_key(&key_prefix, &stayed_key))));
        }
        else {
            changes.push(EntryChange::creating(&to_composite_key(&key_prefix, &stayed_key), new_val.clone()));
        }
    }
}
changes
}

fn to_composite_key(prefix: &Option<String>, subkey: &str) -> String {
    match prefix {
        Some(prefix) => format!("{}/{}", prefix, subkey),
        None => subkey.to_string()
    }
}

pub fn diff_entities(old: &Entity, new: &NotStoredEntity) -> Result<(Vec<EntryChange>, Vec<EntryChange>)>  {
    let property_changes = diff_properties(&old, &new);
    let data_changes = if old.data != new.data { diff_json_maps(&old.data, &new.data)? } else { Vec::new() };
    Ok((data_changes, property_changes))
}
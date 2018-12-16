use crate::entity_metadata::EntityMetadata;
use serde_json::Value;
use std::collections::{HashMap, HashSet};

pub fn check_entity_data_consistency(discriminator: &str, data: &HashMap<String, Value>) -> bool {
    match EntityMetadata::for_discriminator(discriminator) {
        Some(metadata) => check_entity_data_consistency_against_metadata(data, &metadata),
        None => {
            warn!(
                "Failed to get the entity metadata for discriminator {}!",
                discriminator
            );
            false
        }
    }
}

fn check_entity_data_consistency_against_metadata(
    data: &HashMap<String, Value>,
    metadata: &EntityMetadata,
) -> bool {
    for (name, field) in metadata.fields.iter() {
        let _known_field_names: HashSet<&String> = metadata.fields.iter().map(|(n, _)| n).collect();
        if field.required && !data.contains_key(name) {
            warn!(
                "Entity data {:?} are missing the required field {}.",
                data, name
            );
            return false;
        }
    }
    true
}

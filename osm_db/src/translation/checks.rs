use crate::entity_metadata::EntityMetadata;
use serde_json::Value;
use hashbrown::{HashMap, HashSet};

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
    let all_fields = metadata.all_fields();
    let     _known_field_names: HashSet<&String> = all_fields.iter().map(|(n, _)| n).collect();
            for (name, field) in all_fields.iter() {
        if field.required && !data.contains_key(name) {
            warn!(
                "Entity data {:?} are missing the required field {}.",
                data, name
            );
            return false;
        }
    }
    for (name, value) in data.iter() {
        if !_known_field_names.contains(name) {
            info!(
                "The data for entity {} contain an unknown field {} with value {}.",
                metadata.discriminator, name, value
            );
        }
    }
    true
}

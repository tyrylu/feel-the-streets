use crate::entity_metadata::EntityMetadata;
use super::record::TranslationRecord;
use hashbrown::{HashMap, HashSet};
use serde_json::Value;

pub fn check_entity_data_consistency(discriminator: &str, data: &HashMap<String, Value>, mut record: &mut TranslationRecord) -> bool {
    match EntityMetadata::for_discriminator(discriminator) {
        Some(metadata) => check_entity_data_consistency_against_metadata(data, &metadata, &mut record),
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
    record: &mut TranslationRecord,
) -> bool {
    let all_fields = metadata.all_fields();
    let _known_field_names: HashSet<&String> = all_fields.iter().map(|(n, _)| n).collect();
    for (name, field) in all_fields.iter() {
        if field.required && !data.contains_key(name) {
            record.record_missing_required_field(&metadata.discriminator, &name);
                        return false;
        }
    }
    for (name, value) in data.iter() {
        if !_known_field_names.contains(name) {
            record.record_unknown_field(&metadata.discriminator, &name, &value.to_string());
        }
    }
    true
}

use crate::entity_metadata::EntityMetadata;
use linked_hash_map::LinkedHashMap;
use hashbrown::HashMap;
use osm_api::object::OSMObject;
use serde_yaml;
use std::fs::File;

lazy_static! {
    static ref TRANSLATION_SPECS: LinkedHashMap<String, TranslationSpec> = {
        let fp =
            File::open("translation_specs.yml").expect("Failed to open the translation specs file");
        serde_yaml::from_reader::<_, _>(fp).expect("Failed to deserialize the specs.")
    };
}

fn compare_values<F: Fn(&str, &str) -> bool>(
    candidates: &HashMap<String, Vec<String>>,
    tags: &HashMap<String, String>,
    values_comparer: F,
) -> bool {
    for (prop, values) in candidates {
        if !tags.contains_key(prop) {
            continue;
        }
        for val in values {
            if values_comparer(&tags[prop], &val) {
                trace!("Value comparison succeeded for value of key {} with value {}.", prop, val);
                return true;
            }
        }
    }
    false
}

#[derive(Deserialize, Clone, Debug)]
#[serde(untagged)]
pub enum AcceptanceCondition {
    HasProperty {
        has_property: Vec<String>,
    },
    PropertyEquals {
        property_equals: HashMap<String, Vec<String>>,
    },
    PropertyDoesNotEqual {
        property_does_not_equal: HashMap<String, Vec<String>>,
    },
}

impl AcceptanceCondition {
    pub fn evaluate_on(&self, object: &OSMObject) -> bool {
        use self::AcceptanceCondition::*;
        match self {
            HasProperty { has_property } => {
                for prop in has_property {
                    if object.tags.contains_key(prop) {
                        trace!("Matched, object has property {}.", prop);
                        return true;
                    }
                }
            }
            PropertyEquals { property_equals } => {
                return compare_values(&property_equals, &object.tags, |x, y| x == y);
            }
            PropertyDoesNotEqual {
                property_does_not_equal,
            } => {
                return compare_values(&property_does_not_equal, &object.tags, |x, y| x != y);
            }
        }
        false
    }
}

#[derive(Deserialize, Clone)]
pub struct TranslationSpec {
    pub address_aware: Option<bool>,
    pub renames: HashMap<String, String>,
    pub unprefixes: Vec<String>,
    pub replaces_property_value: HashMap<String, HashMap<String, String>>,
    accepts_when: Vec<AcceptanceCondition>,
}

impl TranslationSpec {
    fn is_applycable_for(&self, object: &OSMObject) -> bool {
        for condition in &self.accepts_when {
            trace!("Trying condition {:?} on object {:?}", condition, object);
            if condition.evaluate_on(&object) {
                return true;
            }
        }
        false
    }

    fn for_discriminator(discriminator: &str) -> Option<&Self> {
        TRANSLATION_SPECS.get(discriminator)
    }

    pub fn for_object(object: &OSMObject) -> Option<(String, Self)> {
        for (generates, spec) in TRANSLATION_SPECS.iter() {
            if spec.is_applycable_for(&object) {
                trace!("Trying {}.", generates);
                let metadata = EntityMetadata::for_discriminator(&generates)
                    .expect("Entity and translation spec identifier mismatch.");
                if let Some(parent) = metadata.parent_metadata() {
                    if parent.discriminator != "OSMEntity" {
                        let parent_spec = TranslationSpec::for_discriminator(&parent.discriminator)
                            .expect("Parent has no translation specification.");
                        if !parent_spec.is_applycable_for(&object) {
                            trace!("Parent spec not applicable.");
                            continue;
                        }
                    }
                }
                return Some((generates.clone(), spec.clone()));
            }
        }
        None
    }
}

use crate::entity_metadata::EntityMetadata;
use crate::file_finder;
use hashbrown::HashMap;
use indexmap::IndexMap;
use log::trace;
use once_cell::sync::Lazy;
use osm_api::object::OSMObject;
use serde::Deserialize;
use std::fs::File;

static TRANSLATION_SPECS: Lazy<IndexMap<String, TranslationSpec>> = Lazy::new(|| {
    let specs_file = file_finder::find_file_in_current_or_exe_dir("translation_specs.yml")
        .expect("Could not find translation_specs.yml");
    let fp = File::open(specs_file).expect("Failed to open the translation specs file");
    serde_yaml::from_reader::<_, _>(fp).expect("Failed to deserialize the specs.")
});

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
            if values_comparer(&tags[prop], val) {
                trace!(
                    "Value comparison succeeded for value of key {} with value {}.",
                    prop,
                    val
                );
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
                return compare_values(property_equals, &object.tags, |x, y| x == y);
            }
            PropertyDoesNotEqual {
                property_does_not_equal,
            } => {
                return compare_values(property_does_not_equal, &object.tags, |x, y| x != y);
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
            if condition.evaluate_on(object) {
                return true;
            }
        }
        false
    }

    fn for_discriminator(discriminator: &str) -> Option<&Self> {
        TRANSLATION_SPECS.get(discriminator)
    }

    pub fn all_relevant_for(discriminator: &str) -> Vec<Self> {
        let mut specs = vec![];
        let mut current_metadata =
            EntityMetadata::for_discriminator(discriminator).expect("No metadata of an entity.");
        loop {
            let discriminator = current_metadata.discriminator;
            if discriminator == "OSMEntity" {
                break; // It has no parent and no translation spec
            }
            specs.push(
                TranslationSpec::for_discriminator(discriminator)
                    .unwrap_or_else(|| {
                        panic!(
                            "No translation spec for {} found.",
                            current_metadata.discriminator
                        )
                    })
                    .clone(),
            );
            if let Some(parent) = current_metadata.parent_metadata() {
                current_metadata = parent;
            } else {
                break;
            }
        }
        specs
    }

    pub fn primary_discriminator_for_object(object: &OSMObject) -> Option<String> {
        trace!("Looking translation spec for object {:?}", object);
        for (generates, spec) in TRANSLATION_SPECS.iter() {
            if spec.is_applycable_for(object) {
                trace!("{} matched.", generates);
                return Some(generates.clone());
            }
        }
        None
    }
}

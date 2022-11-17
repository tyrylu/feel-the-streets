#![allow(clippy::new_without_default)]
use crate::Result;
use osm_api::object::OSMObject;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;

#[derive(Serialize, Deserialize)]
pub struct TranslationRecord {
    type_violations: HashMap<String, HashMap<String, Vec<String>>>,
    missing_enum_members: HashMap<String, HashMap<String, u32>>,
    unknown_fields: HashMap<String, HashMap<String, Vec<String>>>,
    missing_required_fields: HashMap<String, HashMap<String, u32>>,
    potentially_interesting_objects: Vec<OSMObject>,
    current_field: Option<String>,
    current_discriminator: Option<String>,
}

impl TranslationRecord {
    pub fn new() -> Self {
        TranslationRecord {
            type_violations: HashMap::new(),
            missing_enum_members: HashMap::new(),
            unknown_fields: HashMap::new(),
            missing_required_fields: HashMap::new(),
            potentially_interesting_objects: Vec::new(),
            current_discriminator: None,
            current_field: None,
        }
    }

    pub fn add_potentially_interesting_object(&mut self, object: OSMObject) {
        self.potentially_interesting_objects.push(object);
    }

    pub fn set_current_discriminator(&mut self, discriminator: &str) {
        self.current_discriminator = Some(discriminator.to_string());
    }

    pub fn set_current_field(&mut self, field: &str) {
        self.current_field = Some(field.to_string());
    }

    pub fn record_missing_enum_member(&mut self, enum_name: &str, member: &str) {
        *(self
            .missing_enum_members
            .entry(enum_name.to_string())
            .or_insert_with(HashMap::new)
            .entry(member.to_string())
            .or_insert(0)) += 1;
    }

    pub fn record_type_violation(&mut self, value: &str) {
        let discriminator = self
            .current_discriminator
            .as_ref()
            .expect("You should set a discriminator first.");
        let field = self
            .current_field
            .as_ref()
            .expect("You should set a current field first.");
        self.type_violations
            .entry(discriminator.to_string())
            .or_insert_with(HashMap::new)
            .entry(field.to_string())
            .or_insert_with(Vec::new)
            .push(value.to_string());
    }
    pub fn record_missing_required_field(&mut self, discriminator: &str, field: &str) {
        *(self
            .missing_required_fields
            .entry(discriminator.to_string())
            .or_insert_with(HashMap::new)
            .entry(field.to_string())
            .or_insert(0)) += 1;
    }

    pub fn record_unknown_field(&mut self, discriminator: &str, field: &str, value: &str) {
        self.unknown_fields
            .entry(discriminator.to_string())
            .or_insert_with(HashMap::new)
            .entry(field.to_string())
            .or_insert_with(Vec::new)
            .push(value.to_string());
    }

    pub fn save_to_file(&self, path: &str) -> Result<()> {
        let serialized = serde_json::to_string(&self)?;
        let mut fp = File::create(path)?;
        write!(fp, "{}", serialized)?;
        Ok(())
    }

    pub fn merge_to(mut self, target: &mut Self) {
        target
            .potentially_interesting_objects
            .append(&mut self.potentially_interesting_objects);
        for (discriminator, missing) in self.missing_required_fields.into_iter() {
            let target_fields = target
                .missing_required_fields
                .entry(discriminator)
                .or_insert_with(HashMap::new);
            for (field, occurrences) in missing.into_iter() {
                *(target_fields.entry(field).or_insert(0)) += occurrences;
            }
        }
        for (discriminator, unknown) in self.unknown_fields.into_iter() {
            let target_unknown = target
                .unknown_fields
                .entry(discriminator)
                .or_insert_with(HashMap::new);
            for (field, mut values) in unknown.into_iter() {
                target_unknown
                    .entry(field)
                    .or_insert_with(Vec::new)
                    .append(&mut values);
            }
        }
        for (discriminator, members) in self.missing_enum_members.into_iter() {
            let other_missing = target
                .missing_enum_members
                .entry(discriminator)
                .or_insert_with(HashMap::new);
            for (member, occurrences) in members.into_iter() {
                *other_missing.entry(member).or_insert(0) += occurrences;
            }
        }
        for (discriminator, violations) in self.type_violations.into_iter() {
            let other_violations = target
                .type_violations
                .entry(discriminator)
                .or_insert_with(HashMap::new);
            for (field, mut values) in violations.into_iter() {
                other_violations
                    .entry(field)
                    .or_insert_with(Vec::new)
                    .append(&mut values);
            }
        }
    }
}

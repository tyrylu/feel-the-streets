#![allow(clippy::new_without_default)]
use crate::Result;
use osm_api::object::OSMObject;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;

/// A flat, sorted entry used in the review report.
pub struct SortedEntry {
    pub key: String,
    pub count: usize,
    pub examples: Vec<String>,
}

/// All data needed to render a review report, with items pre-sorted by count descending.
pub struct TranslationSummary {
    pub missing_enum_members: Vec<SortedEntry>,
    pub type_violations: Vec<SortedEntry>,
    pub unknown_fields: Vec<SortedEntry>,
    pub missing_required_fields: Vec<SortedEntry>,
    /// Each entry's `key` is a tag-combination fingerprint, `count` is occurrences.
    pub interesting_object_combinations: Vec<SortedEntry>,
}

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
            .or_default()
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
            .or_default()
            .entry(field.to_string())
            .or_default()
            .push(value.to_string());
    }
    pub fn record_missing_required_field(&mut self, discriminator: &str, field: &str) {
        *(self
            .missing_required_fields
            .entry(discriminator.to_string())
            .or_default()
            .entry(field.to_string())
            .or_insert(0)) += 1;
    }

    pub fn record_unknown_field(&mut self, discriminator: &str, field: &str, value: &str) {
        self.unknown_fields
            .entry(discriminator.to_string())
            .or_default()
            .entry(field.to_string())
            .or_default()
            .push(value.to_string());
    }

    pub fn summarize(&self) -> TranslationSummary {
        // Helper: flatten a HashMap<String, HashMap<String, Vec<String>>> into sorted entries.
        fn flatten_vec_map(
            map: &HashMap<String, HashMap<String, Vec<String>>>,
        ) -> Vec<SortedEntry> {
            let mut entries: Vec<SortedEntry> = map
                .iter()
                .flat_map(|(outer, inner)| {
                    inner.iter().map(move |(inner_key, values)| SortedEntry {
                        key: format!("{outer}.{inner_key}"),
                        count: values.len(),
                        examples: {
                            let mut seen = std::collections::HashSet::new();
                            let mut uniq: Vec<String> = Vec::new();
                            for v in values {
                                if seen.insert(v.clone()) {
                                    uniq.push(v.clone());
                                }
                            }
                            uniq.truncate(5);
                            uniq
                        },
                    })
                })
                .collect();
            entries.sort_by(|a, b| b.count.cmp(&a.count));
            entries
        }

        // Helper: flatten a HashMap<String, HashMap<String, u32>> into sorted entries.
        fn flatten_count_map(
            map: &HashMap<String, HashMap<String, u32>>,
            sep: char,
        ) -> Vec<SortedEntry> {
            let mut entries: Vec<SortedEntry> = map
                .iter()
                .flat_map(|(outer, inner)| {
                    inner.iter().map(move |(inner_key, &count)| SortedEntry {
                        key: format!("{outer}{sep}{inner_key}"),
                        count: count as usize,
                        examples: vec![],
                    })
                })
                .collect();
            entries.sort_by(|a, b| b.count.cmp(&a.count));
            entries
        }

        // Interesting objects: build tag-combination fingerprints.
        let mut combo_counts: HashMap<String, usize> = HashMap::new();
        for obj in &self.potentially_interesting_objects {
            let mut pairs: Vec<String> = obj
                .tags
                .iter()
                .map(|(k, v)| format!("{k}={v}"))
                .collect();
            pairs.sort();
            let fingerprint = pairs.join(", ");
            *combo_counts.entry(fingerprint).or_insert(0) += 1;
        }
        let mut interesting: Vec<SortedEntry> = combo_counts
            .into_iter()
            .map(|(key, count)| SortedEntry {
                key,
                count,
                examples: vec![],
            })
            .collect();
        interesting.sort_by(|a, b| b.count.cmp(&a.count));

        TranslationSummary {
            missing_enum_members: flatten_count_map(&self.missing_enum_members, ':'),
            type_violations: flatten_vec_map(&self.type_violations),
            unknown_fields: flatten_vec_map(&self.unknown_fields),
            missing_required_fields: flatten_count_map(&self.missing_required_fields, '.'),
            interesting_object_combinations: interesting,
        }
    }

    pub fn save_to_file(&self, path: &str) -> Result<()> {
        let serialized = serde_json::to_string(&self)?;
        let mut fp = File::create(path)?;
        write!(fp, "{serialized}")?;
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
                .or_default();
            for (field, occurrences) in missing.into_iter() {
                *(target_fields.entry(field).or_insert(0)) += occurrences;
            }
        }
        for (discriminator, unknown) in self.unknown_fields.into_iter() {
            let target_unknown = target.unknown_fields.entry(discriminator).or_default();
            for (field, mut values) in unknown.into_iter() {
                target_unknown.entry(field).or_default().append(&mut values);
            }
        }
        for (discriminator, members) in self.missing_enum_members.into_iter() {
            let other_missing = target
                .missing_enum_members
                .entry(discriminator)
                .or_default();
            for (member, occurrences) in members.into_iter() {
                *other_missing.entry(member).or_insert(0) += occurrences;
            }
        }
        for (discriminator, violations) in self.type_violations.into_iter() {
            let other_violations = target.type_violations.entry(discriminator).or_default();
            for (field, mut values) in violations.into_iter() {
                other_violations
                    .entry(field)
                    .or_default()
                    .append(&mut values);
            }
        }
    }
}

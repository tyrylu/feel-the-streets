use crate::entity_metadata::EntityMetadata;
use crate::entity_metadata::Enum;
use super::record::TranslationRecord;
use hashbrown::HashMap;
use serde_json::{Number, Value};
use uom::si::f64::{Length, Mass};
use uom::si::length::meter;
use uom::si::mass::ton;

pub fn convert_address(tags: &HashMap<String, String>) -> (HashMap<String, String>, Vec<&str>) {
    let mut address_field_names = vec![];
    let mut address_fields = HashMap::new();
    for (key, val) in tags.iter() {
        if key.starts_with("addr:") {
            address_field_names.push(key.as_str());
            address_fields.insert(key[5..].to_string(), val.clone());
        }
    }
    (address_fields, address_field_names)
}

pub fn convert_field_value(raw_value: &str, value_type: &str, mut record: &mut TranslationRecord) -> Option<Value> {
    match value_type {
        "str" | "Address" => Some(Value::String(raw_value.to_string())),
        "int" => convert_int(&raw_value, &mut record),
        "bool" => convert_bool(&raw_value, &mut record),
        "float" => convert_float(&raw_value, &mut record),
        "tons" => convert_to_tons(&raw_value, &mut record),
        "meters" => convert_to_meters(&raw_value, &mut record),
        _ => {
            if let Some(enum_spec) = Enum::with_name(&value_type) {
                convert_value_of_enum(&raw_value, &enum_spec, &mut record)
            } else {
                panic!(format!("Failed to handle type specifier {}.", value_type))
            }
        }
    }
}

pub fn convert_entity_data(
    discriminator: &str,
    entity_data: &HashMap<String, String>, mut record: &mut TranslationRecord
) -> HashMap<String, Value> {
    record.set_current_discriminator(discriminator);
    let all_fields = EntityMetadata::for_discriminator(discriminator)
        .expect("Metadata not found?")
        .all_fields();
    let mut converted_data = HashMap::new();
    for (key, value) in entity_data.iter() {
        record.set_current_field(key);
        let type_name = all_fields.get(key).map(|f| f.type_name.as_str()).unwrap_or("str");
                if let Some(converted) = convert_field_value(&value, &type_name, &mut record) {
            converted_data.insert(key.clone(), converted);
        }     }
    converted_data
}

fn convert_value_of_enum(value: &str, enum_spec: &Enum, record: &mut TranslationRecord) -> Option<Value> {
    if let Some(num) = enum_spec.value_for_name(&value) {
        Some(Value::Number(Number::from(*num)))
    } else {
        record.record_missing_enum_member(&enum_spec.name, &value);
        None
    }
}

fn convert_int(value: &str, record: &mut TranslationRecord) -> Option<Value> {
    match value.parse::<i64>() {
        Ok(val) => Some(Value::Number(Number::from(val))),
        Err(_) => {
            record.record_type_violation(&value);
            None
        }
    }
}

fn convert_bool(value: &str, record: &mut TranslationRecord) -> Option<Value> {
    match value {
        "yes" | "true" => Some(Value::Bool(true)),
        "no" | "false" => Some(Value::Bool(false)),
        _ => {
            record.record_type_violation(value);
            None
        }
    }
}

fn construct_json_f64(value: f64) -> Option<Value> {
    Some(Value::Number(
        Number::from_f64(value).expect("Json number construction failure."),
    ))
}

fn convert_float(value: &str, record: &mut TranslationRecord) -> Option<Value> {
    match value.parse::<f64>() {
        Ok(val) => construct_json_f64(val),
        Err(_) => {
            record.record_type_violation(&value);
            None
        }
    }
}

fn split_unit_spec<'a>(spec: &'a str, record: &mut TranslationRecord) -> Option<(f64, Option<&'a str>)> {
    let parts: Vec<&str> = spec.split(' ').collect();
    if parts.len() > 2 {
        record.record_type_violation(&spec);
        None
    } else if let Ok(num) = parts[0].parse::<f64>() {
        Some((num, parts.get(1).cloned()))
    } else {
        record.record_type_violation(&spec);
        None
    }
}

fn convert_to_tons(value: &str, mut record: &mut TranslationRecord) -> Option<Value> {
    let (magnitude, unit_str) = split_unit_spec(&value, &mut record)?;
    match unit_str {
        None => construct_json_f64(magnitude),
        Some(unit) => match unit {
            "t" => construct_json_f64(Mass::new::<ton>(magnitude).get::<ton>()),
            _ => {
                record.record_type_violation(&value);
                None
            }
        },
    }
}

fn convert_to_meters(value: &str, mut record: &mut TranslationRecord) -> Option<Value> {
    let (magnitude, unit_str) = split_unit_spec(&value, &mut record)?;
    match unit_str {
        None => construct_json_f64(magnitude),
        Some(unit) => match unit {
            "m" => construct_json_f64(Length::new::<meter>(magnitude).get::<meter>()),
            _ => {
                record.record_type_violation(&value);
                None
            }
        },
    }
}

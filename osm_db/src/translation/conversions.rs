use crate::entity_metadata::EntityMetadata;
use crate::entity_metadata::Enum;
use serde_json::{Number, Value};
use std::collections::HashMap;
use uom::si::f64::{Length, Mass};
use uom::si::length::meter;
use uom::si::mass::ton;

pub fn convert_entity_data(
    discriminator: &str,
    entity_data: &HashMap<String, String>,
) -> HashMap<String, Value> {
    let metadata = EntityMetadata::for_discriminator(discriminator).expect("Metadata not found?");
    let mut converted_data = HashMap::new();
    for (key, value) in entity_data.iter() {
        let type_name = match metadata.fields.get(key) {
            Some(field) => field.type_name.as_str(),
            None => "str",
        };
        let converted_value = match type_name {
            "str" => Some(Value::String(value.clone())),
            "int" => convert_int(&value),
            "bool" => convert_bool(&value),
            "float" => convert_float(&value),
            "tons" => convert_to_tons(&value),
            "meters" => convert_to_meters(&value),
            _ => {
                if let Some(enum_spec) = Enum::with_name(&type_name) {
                    convert_value_of_enum(&value, &enum_spec)
                } else {
                    panic!(format!("Failed to handle type specifier {}.", type_name))
                }
            }
        };
        if let Some(converted) = converted_value {
            converted_data.insert(key.clone(), converted);
        } else {
            warn!(
                "Omitting inclusion of property {} because of a conversion failure.",
                key
            );
        }
    }
    converted_data
}

fn convert_value_of_enum(value: &str, enum_spec: &Enum) -> Option<Value> {
    if let Some(num) = enum_spec.value_for_name(&value) {
        Some(Value::Number(Number::from(*num)))
    } else {
        warn!(
            "The enum {} does not define the member {}.",
            enum_spec.name, value
        );
        None
    }
}

fn convert_int(value: &str) -> Option<Value> {
    match value.parse::<i64>() {
        Ok(val) => Some(Value::Number(Number::from(val))),
        Err(e) => {
            warn!("Failed to parse {} as an integer, error {}", value, e);
            None
        }
    }
}

fn convert_bool(value: &str) -> Option<Value> {
    match value {
        "yes" => Some(Value::Bool(true)),
        "no" => Some(Value::Bool(false)),
        _ => {
            warn!("Could not interpret {} as a bool.", value);
            None
        }
    }
}

fn construct_json_f64(value: f64) -> Option<Value> {
    Some(Value::Number(
        Number::from_f64(value).expect("Json number construction failure."),
    ))
}

fn convert_float(value: &str) -> Option<Value> {
    match value.parse::<f64>() {
        Ok(val) => construct_json_f64(val),
        Err(e) => {
            warn!("Failed to parse {} as a float, error {}", value, e);
            None
        }
    }
}

fn split_unit_spec(spec: &str) -> Option<(f64, Option<&str>)> {
    let parts: Vec<&str> = spec.split(' ').collect();
    if parts.len() > 2 {
        warn!("Unit specification {} is not valid.", spec);
        None
    } else if let Ok(num) = parts[0].parse::<f64>() {
        Some((num, parts.get(1).cloned()))
    } else {
        warn!(
            "The magnitude of the unit specification {} could not be parsed as a f64.",
            spec
        );
        None
    }
}

fn convert_to_tons(value: &str) -> Option<Value> {
    let (magnitude, unit_str) = split_unit_spec(&value)?;
    match unit_str {
        None => construct_json_f64(magnitude),
        Some(unit) => match unit {
            "t" => construct_json_f64(Mass::new::<ton>(magnitude).get::<ton>()),
            _ => {
                warn!("Unsupported unit specifier {}.", unit);
                None
            }
        },
    }
}
fn convert_to_meters(value: &str) -> Option<Value> {
    let (magnitude, unit_str) = split_unit_spec(&value)?;
    match unit_str {
        None => construct_json_f64(magnitude),
        Some(unit) => match unit {
            "m" => construct_json_f64(Length::new::<meter>(magnitude).get::<meter>()),
            _ => {
                warn!("Unsupported unit specifier {}.", unit);
                None
            }
        },
    }
}

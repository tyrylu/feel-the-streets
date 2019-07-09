use pyo3::prelude::*;
use serde_json::Value;
use std::collections::HashMap;

pub fn convert_value(val: &Value, py: &Python) -> PyObject {
    match val {
        Value::Bool(b) => b.into_object(*py),
        Value::String(str) => str.into_object(*py),
        Value::Number(n) => {
            if n.is_i64() {
                n.as_i64().unwrap().into_object(*py)
            } else {
                n.as_f64().unwrap().into_object(*py)
            }
        }
        Value::Array(vals) => vals
            .iter()
            .map(|v| convert_value(v, &py))
            .collect::<Vec<PyObject>>()
            .into_object(*py),
        Value::Object(o) => {
            let mut ret = HashMap::new();
            for (k, v) in o.iter() {
                ret.insert(k, convert_value(v, &py));
            }
            ret.into_object(*py)
        }
        Value::Null => py.None(),
    }
}

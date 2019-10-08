use osm_db::ToSql;
use pyo3::prelude::*;
use serde_json::Value;
use std::collections::HashMap;
use std::rc::Rc;

pub fn convert_value(val: &Value, py: &Python) -> PyObject {
    match val {
        Value::Bool(b) => if *b { true.into_py(*py) } else { false.into_py(*py) },
        Value::String(str) => str.into_py(*py),
        Value::Number(n) => {
            if n.is_i64() {
                n.as_i64().unwrap().into_py(*py)
            } else {
                n.as_f64().unwrap().into_py(*py)
            }
        }
        Value::Array(vals) => vals
            .iter()
            .map(|v| convert_value(v, &py))
            .collect::<Vec<PyObject>>()
            .into_py(*py),
        Value::Object(o) => {
            let mut ret = HashMap::new();
            for (k, v) in o.iter() {
                ret.insert(k, convert_value(v, &py));
            }
            ret.into_py(*py)
        }
        Value::Null => py.None(),
    }
}

pub fn convert_object_for_query(obj: &PyObject, py: Python) -> Option<Rc<dyn ToSql>> {
    if let Ok(val) = obj.extract::<String>(py) {
        return Some(Rc::new(val));
    }
    if let Ok(val) = obj.extract::<i64>(py) {
        return Some(Rc::new(val));
    }
    if let Ok(val) = obj.extract::<f64>(py) {
        return Some(Rc::new(val));
    }

    None
}

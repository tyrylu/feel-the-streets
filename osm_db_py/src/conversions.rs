use osm_db::ToSql;
use pyo3::prelude::*;
use pyo3::IntoPyObjectExt;
use serde_json::Value;
use std::collections::HashMap;
use std::sync::Arc;

pub fn convert_value(val: &Value, py: &Python) -> Py<PyAny> {
    match val {
        Value::Bool(b) => (*b).into_py_any(*py).unwrap(),
        Value::String(str) => str.into_py_any(*py).unwrap(),
        Value::Number(n) => {
            if n.is_i64() {
                n.as_i64().unwrap().into_py_any(*py).unwrap()
            } else {
                n.as_f64().unwrap().into_py_any(*py).unwrap()
            }
        }
        Value::Array(vals) => vals
            .iter()
            .map(|v| convert_value(v, py))
            .collect::<Vec<Py<PyAny>>>()
            .into_py_any(*py).unwrap(),
        Value::Object(o) => {
            let mut ret = HashMap::new();
            for (k, v) in o.iter() {
                ret.insert(k, convert_value(v, py));
            }
            ret.into_py_any(*py).unwrap()
        }
        Value::Null => py.None().into_py_any(*py).unwrap(),
    }
}

pub fn convert_object_for_query(
    obj: &PyObject,
    py: Python,
) -> Option<Arc<dyn ToSql + Send + Sync>> {
    if let Ok(val) = obj.extract::<String>(py) {
        return Some(Arc::new(val));
    }
    if let Ok(val) = obj.extract::<i64>(py) {
        return Some(Arc::new(val));
    }
    if let Ok(val) = obj.extract::<f64>(py) {
        return Some(Arc::new(val));
    }

    None
}

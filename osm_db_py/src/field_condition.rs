use osm_db::entities_query_condition::FieldCondition;
use pyo3::prelude::*;

#[pyclass(name="FieldCondition")]
pub struct PyFieldCondition {
    pub inner: FieldCondition,
}

impl PyFieldCondition {
    pub fn new(condition: FieldCondition) -> Self {
        Self { inner: condition }
    }
}

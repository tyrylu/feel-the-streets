use osm_db::entities_query_condition::FieldCondition;
use pyo3::prelude::*;

#[pyclass(name = "FieldCondition")]
pub struct PyFieldCondition {
    pub inner: FieldCondition,
}

impl PyFieldCondition {
    pub fn new(condition: FieldCondition) -> Self {
        Self { inner: condition }
    }
}

#[pymethods]
impl PyFieldCondition {
pub fn or_(&self, right: &Self) -> Self {
        Self::new(FieldCondition::Or{left: Box::new(self.inner.clone()), right: Box::new(right.inner.clone())})
    }

}
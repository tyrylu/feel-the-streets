use crate::conversions;
use osm_db::entity::Entity;
use pyo3::basic::CompareOp;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

#[pyclass(name = "Entity")]
pub struct PyEntity {
    pub(crate) inner: Entity,
}

#[pymethods]
impl PyEntity {
    #[getter]
    pub fn id(&self) -> &str {
        self.inner.id.as_str()
    }

    #[getter]
    pub fn effective_width(&self) -> Option<f64> {
        self.inner.effective_width
    }

    #[getter]
    pub fn geometry(&self) -> PyObject {
        Python::with_gil(|py| PyBytes::new(py, &self.inner.geometry).into())
    }

    #[getter]
    pub fn discriminator(&self) -> &str {
        self.inner.discriminator.as_str()
    }

    pub fn value_of_field(&mut self, key: &str) -> Py<PyAny> {
        Python::with_gil(|py| conversions::convert_value(self.inner.value_of_field(key), &py))
    }

    pub fn defined_field_names(&mut self) -> Vec<&String> {
        self.inner.defined_field_names()
    }

    #[getter]
    pub fn is_road_like(&self) -> bool {
        self.inner.is_road_like()
    }

    fn __hash__(&self) -> PyResult<u64> {
        let mut hasher = DefaultHasher::new();
        self.inner.id.hash(&mut hasher);
        let hash = hasher.finish();
        Ok(hash)
    }

    fn __richcmp__(&self, other: PyRef<Self>, op: CompareOp) -> PyResult<bool> {
        let id1 = &self.inner.id;
        let id2 = &other.inner.id;
        match op {
            CompareOp::Eq => Ok(id1 == id2),
            CompareOp::Ne => Ok(id1 != id2),
            CompareOp::Lt => Ok(id1 < id2),
            CompareOp::Le => Ok(id1 <= id2),
            CompareOp::Gt => Ok(id1 > id2),
            CompareOp::Ge => Ok(id1 >= id2),
        }
    }
}

use crate::conversions;
use osm_db::entity::Entity;
use pyo3::prelude::*;

#[pyclass(name=Entity)]
pub struct PyEntity {
    pub(crate) inner: Entity,
}

#[pymethods]
impl PyEntity {
    #[getter]
    pub fn id(&self) -> i32 {
        self.inner.id
    }

    #[getter]
    pub fn effective_width(&self) -> Option<f64> {
        self.inner.effective_width
    }

    #[getter]
    pub fn geometry(&self) -> &str {
        self.inner.geometry.as_str()
    }

    #[getter]
    pub fn discriminator(&self) -> &str {
        self.inner.discriminator.as_str()
    }

    pub fn value_of_field(&mut self, key: &str) -> PyObject {
        let gil = Python::acquire_gil();
        let py = gil.python();
        conversions::convert_value(self.inner.value_of_field(key), &py)
    }
}

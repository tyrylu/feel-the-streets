use crate::conversions;
use osm_db::entity::Entity;
use pyo3::basic::CompareOp;
use pyo3::class::basic::PyObjectProtocol;
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
    pub fn geometry(&self) -> Vec<u8> {
        self.inner.geometry.clone()
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

    #[getter]
    pub fn defined_field_names(&mut self) -> Vec<&String> {
        self.inner.defined_field_names()
    }
}

#[pyproto]
impl PyObjectProtocol for PyEntity {
    fn __hash__(&'p self) -> PyResult<isize> {
        Ok(self.id() as isize)
    }

    fn __richcmp__(&self, other: &Self, op: CompareOp) -> PyResult<bool> {
        let id1 = self.id();
        let id2 = other.id();
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

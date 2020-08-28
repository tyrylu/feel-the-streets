use osm_db::entity_metadata::{EntityMetadata, Enum, Field};
use pyo3::exceptions;
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[pyclass(name=EntityMetadata)]
pub struct PyEntityMetadata {
    inner: EntityMetadata,
}
#[pymethods]
impl PyEntityMetadata {
    #[staticmethod]
    pub fn for_discriminator(discriminator: &str) -> PyResult<Self> {
        match EntityMetadata::for_discriminator(discriminator) {
            Some(metadata) => Ok(Self { inner: metadata }),
            None => Err(exceptions::KeyError::py_err(format!(
                "No entity with discriminator {}.",
                discriminator
            ))),
        }
    }
    #[getter]
    pub fn discriminator(&self) -> &str {
        self.inner.discriminator.as_str()
    }

    #[getter]
    pub fn fields(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        for (k, v) in &self.inner.fields {
            dict.set_item(k, Py::new(py, PyField { inner: v.clone() })?)?;
        }
        Ok(dict.into())
    }

    #[getter]
    pub fn long_display_template(&self) -> Option<&String> {
        self.inner.long_display_template.as_ref()
    }

    #[getter]
    pub fn short_display_template(&self) -> Option<&String> {
        self.inner.short_display_template.as_ref()
    }

    #[getter]
    pub fn all_fields(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        for (k, f) in self.inner.all_fields() {
            dict.set_item(k, Py::new(py, PyField { inner: f })?)?;
        }
        Ok(dict.into())
    }

    #[getter]
    pub fn parent_metadata(&self) -> Option<Self> {
        self.inner.parent_metadata().map(|m| Self { inner: m })
    }
}

#[pyclass(name=Field)]
pub struct PyField {
    inner: Field,
}

#[pymethods]
impl PyField {
    #[getter]
    pub fn type_name(&self) -> &str {
        self.inner.type_name.as_str()
    }

    #[getter]
    pub fn required(&self) -> bool {
        self.inner.required
    }
}

#[pyclass(name=Enum)]
pub struct PyEnum {
    inner: Enum,
}

#[pymethods]
impl PyEnum {
    #[staticmethod]
    pub fn all_known() -> Vec<&'static String> {
        Enum::all_known()
    }

    #[staticmethod]
    pub fn with_name(name: &str) -> Option<Self> {
        Enum::with_name(name).map(|e| PyEnum { inner: e })
    }

    #[getter]
    pub fn name(&self) -> &str {
        self.inner.name.as_str()
    }

    pub fn value_for_name(&self, name: &str) -> Option<i32> {
        self.inner.value_for_name(name).copied()
    }
    pub fn name_for_value(&self, value: i32) -> Option<&'static String> {
        self.inner.name_for_value(value)
    }
}

use crate::conversions;
use crate::field_condition::PyFieldCondition;
use osm_db::entities_query_condition::{Condition, FieldCondition};
use pyo3::exceptions;
use pyo3::prelude::*;

#[pyclass]
pub struct FieldNamed {
    name: String,
}

#[pymethods]
impl FieldNamed {
    #[new]
    pub fn new(name: String) -> Self {
        FieldNamed { name }
    }

    pub fn eq(&self, val: PyObject, py: Python) -> PyResult<PyFieldCondition> {
        if let Some(converted) = conversions::convert_object_for_query(&val, py) {
            Ok(PyFieldCondition::new(FieldCondition::new(
                self.name.clone(),
                Condition::Eq { value: converted },
            )))
        } else {
            Err(exceptions::TypeError::py_err("Unsupported type for query"))
        }
    }

    pub fn neq(&self, val: PyObject, py: Python) -> PyResult<PyFieldCondition> {
        if let Some(converted) = conversions::convert_object_for_query(&val, py) {
            Ok(PyFieldCondition::new(FieldCondition::new(
                self.name.clone(),
                Condition::Neq { value: converted },
            )))
        } else {
            Err(exceptions::TypeError::py_err("Unsupported type for query"))
        }
    }
    pub fn lt(&self, val: PyObject, py: Python) -> PyResult<PyFieldCondition> {
        if let Some(converted) = conversions::convert_object_for_query(&val, py) {
            Ok(PyFieldCondition::new(FieldCondition::new(
                self.name.clone(),
                Condition::Lt { value: converted },
            )))
        } else {
            Err(exceptions::TypeError::py_err("Unsupported type for query"))
        }
    }

    pub fn le(&self, val: PyObject, py: Python) -> PyResult<PyFieldCondition> {
        if let Some(converted) = conversions::convert_object_for_query(&val, py) {
            Ok(PyFieldCondition::new(FieldCondition::new(
                self.name.clone(),
                Condition::Le { value: converted },
            )))
        } else {
            Err(exceptions::TypeError::py_err("Unsupported type for query"))
        }
    }
    pub fn gt(&self, val: PyObject, py: Python) -> PyResult<PyFieldCondition> {
        if let Some(converted) = conversions::convert_object_for_query(&val, py) {
            Ok(PyFieldCondition::new(FieldCondition::new(
                self.name.clone(),
                Condition::Gt { value: converted },
            )))
        } else {
            Err(exceptions::TypeError::py_err("Unsupported type for query"))
        }
    }
    pub fn ge(&self, val: PyObject, py: Python) -> PyResult<PyFieldCondition> {
        if let Some(converted) = conversions::convert_object_for_query(&val, py) {
            Ok(PyFieldCondition::new(FieldCondition::new(
                self.name.clone(),
                Condition::Ge { value: converted },
            )))
        } else {
            Err(exceptions::TypeError::py_err("Unsupported type for query"))
        }
    }
    pub fn like(&self, val: PyObject, py: Python) -> PyResult<PyFieldCondition> {
        if let Some(converted) = conversions::convert_object_for_query(&val, py) {
            Ok(PyFieldCondition::new(FieldCondition::new(
                self.name.clone(),
                Condition::Like { value: converted },
            )))
        } else {
            Err(exceptions::TypeError::py_err("Unsupported type for query"))
        }
    }
    pub fn is_null(&self) -> PyFieldCondition {
        PyFieldCondition::new(FieldCondition::new(self.name.clone(), Condition::IsNull))
    }
    pub fn is_not_null(&self) -> PyFieldCondition {
        PyFieldCondition::new(FieldCondition::new(self.name.clone(), Condition::IsNotNull))
    }
}

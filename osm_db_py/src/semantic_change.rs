use osm_db::semantic_change::SemanticChange;
use pyo3::prelude::*;
use pyo3::exceptions;
use crate::dict_change::DictChange;
use serde_json::Value;

#[pyclass(name=SemanticChange)]
pub struct PySemanticChange {
    inner: SemanticChange
}

#[pymethods]
impl PySemanticChange {
    #[staticmethod]
    fn from_json(json: &str) -> PyResult<Py<PySemanticChange>> {
    match serde_json::from_str::<SemanticChange>(json) {
        Ok(change) => {
                let gil = Python ::acquire_gil();
    let py = gil.python();
    Ok(Py::new(py, PySemanticChange {inner: change}).unwrap())
        },
        Err(e) => Err(exceptions::ValueError::py_err(format!("Could not parse json, error: {}", e)))
    }
    }
    #[getter("type")]
    fn change_type(&self) -> i32 {
                match self.inner {
            SemanticChange::Create{..} => crate::CHANGE_CREATE,
            SemanticChange::Update{..} => crate::CHANGE_UPDATE,
            SemanticChange::Remove{..} => crate::CHANGE_REMOVE
        }
    }
    #[getter]
    fn osm_id(&self) -> Option<&str> {
        match &self.inner {
            SemanticChange::Remove{osm_id, ..} | SemanticChange::Update{osm_id, ..} => Some(osm_id),
SemanticChange::Create{..} => None
        }
    }
    #[getter]
    fn data_changes(&self) -> Vec<DictChange> {
        match &self.inner {
            SemanticChange::Update{data_changes, ..} => data_changes.iter().map(|c| DictChange::new(c.clone())).collect(),
            SemanticChange::Remove{..} | SemanticChange::Create{..} => vec![]
        }
    }

    #[getter]
    fn property_changes(&self) -> Vec<DictChange> {
        match &self.inner {
            SemanticChange::Update{property_changes, ..} => property_changes.iter().map(|c| DictChange::new(c.clone())).collect(),
            SemanticChange::Create{geometry, discriminator, data, effective_width} => {
                let mut ret = vec![];
                ret.push(DictChange::creating("discriminator", Value::from(discriminator.clone())));
                ret.push(DictChange::creating("geometry", Value::from(geometry.clone())));
                ret.push(DictChange::creating("data", Value::from(data.clone())));
                if let Some(val) = effective_width {
                ret.push(DictChange::creating("effective_width", Value::from(val.clone())))
                }
                ret
            },
            SemanticChange::Remove{..} => vec![]
        }
    }
}
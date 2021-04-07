use crate::dict_change::DictChange;
use osm_db::semantic_change::SemanticChange;
use pyo3::exceptions;
use pyo3::prelude::*;
use serde_json::Value;

#[pyclass(name = "SemanticChange")]
pub struct PySemanticChange {
    pub(crate) inner: SemanticChange,
}

#[pymethods]
impl PySemanticChange {
    #[staticmethod]
    fn from_serialized(data: &[u8]) -> PyResult<PySemanticChange> {
        match SemanticChange::from_serialized(&data) {
            Ok(change) => Ok(PySemanticChange { inner: change }),
            Err(e) => Err(exceptions::PyValueError::new_err(format!(
                "Could not parse json, error: {}",
                e
            ))),
        }
    }
    #[getter]
    fn get_type(&self) -> i32 {
        match self.inner {
            SemanticChange::RedownloadDatabase => crate::CHANGE_REDOWNLOAD_DATABASE,
            SemanticChange::Create { .. } => crate::CHANGE_CREATE,
            SemanticChange::Update { .. } => crate::CHANGE_UPDATE,
            SemanticChange::Remove { .. } => crate::CHANGE_REMOVE,
        }
    }
    #[getter]
    fn osm_id(&self) -> Option<&str> {
        match &self.inner {
            SemanticChange::Remove { osm_id, .. } | SemanticChange::Update { osm_id, .. } => {
                Some(osm_id)
            }
            SemanticChange::Create { id, .. } => Some(id),
            SemanticChange::RedownloadDatabase => None,
        }
    }
    #[getter]
    fn data_changes(&self) -> Vec<DictChange> {
        match &self.inner {
            SemanticChange::Update { data_changes, .. } => data_changes
                .iter()
                .map(|c| DictChange::new(c.clone()))
                .collect(),
            SemanticChange::Remove { .. }
            | SemanticChange::Create { .. }
            | SemanticChange::RedownloadDatabase => vec![],
        }
    }

    #[getter]
    fn property_changes(&self) -> Vec<DictChange> {
        match &self.inner {
            SemanticChange::Update {
                property_changes, ..
            } => property_changes
                .iter()
                .map(|c| DictChange::new(c.clone()))
                .collect(),
            // We don't need the child_ids in the changelog, they are important, but spamming the changelog with them is pointless.
            SemanticChange::Create {
                id,
                geometry,
                discriminator,
                data,
                effective_width,
                ..
            } => {
                let mut ret = vec![DictChange::creating("id", Value::from(id.as_str())), DictChange::creating(
                    "discriminator",
                    Value::from(discriminator.clone()),
                ), DictChange::creating(
                    "geometry",
                    Value::from(geometry.clone()),
                ), DictChange::creating("data", Value::from(data.clone()))];
                                if let Some(val) = effective_width {
                    ret.push(DictChange::creating("effective_width", Value::from(*val)))
                }
                ret
            }
            SemanticChange::Remove { .. } | SemanticChange::RedownloadDatabase => vec![],
        }
    }
}

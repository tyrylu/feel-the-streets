use crate::dict_change::DictChange;
use crate::ChangeType;
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
        match SemanticChange::from_serialized(data) {
            Ok(change) => Ok(PySemanticChange { inner: change }),
            Err(e) => Err(exceptions::PyValueError::new_err(format!(
                "Could not parse json, error: {e}"
            ))),
        }
    }
    #[getter]
    fn get_type(&self) -> ChangeType {
        use ChangeType::*;
        match self.inner {
            SemanticChange::Create { .. } => Create,
            SemanticChange::Update { .. } => Update,
            SemanticChange::Remove { .. } => Remove,
        }
    }
    #[getter]
    fn osm_id(&self) -> &str {
        self.inner.osm_id()
    }
    #[getter]
    fn data_changes(&self) -> Vec<DictChange> {
        match &self.inner {
            SemanticChange::Update { data_changes, .. } => data_changes
                .iter()
                .map(|c| DictChange::new(c.clone()))
                .collect(),
            SemanticChange::Remove { .. } | SemanticChange::Create { .. } => vec![],
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
                let mut ret = vec![
                    DictChange::creating("id", id.as_str().into()),
                    DictChange::creating("discriminator", discriminator.clone().into()),
                    DictChange::creating("geometry", Value::from(geometry.clone())),
                    DictChange::creating("data", Value::from(data.clone())),
                ];
                if let Some(val) = effective_width {
                    ret.push(DictChange::creating("effective_width", Value::from(*val)))
                }
                ret
            }
            SemanticChange::Remove { .. } => vec![],
        }
    }
}

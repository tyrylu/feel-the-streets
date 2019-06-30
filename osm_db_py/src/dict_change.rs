use pyo3::prelude::*;
use osm_db::semantic_change::EntryChange;
use serde_json::Value;

#[pyclass]
pub struct DictChange {
    inner: EntryChange
}

#[pymethods]
impl DictChange {

    #[getter]
    fn kind(&self) -> i32 {
        match self.inner {
            EntryChange::Create{..} => crate::CHANGE_CREATE,
            EntryChange::Update{..} => crate::CHANGE_UPDATE,
            EntryChange::Remove{..} => crate::CHANGE_REMOVE
        }
    }

    #[getter]
    fn key(&self) -> &str {
        match &self.inner {
            EntryChange::Create{key,..} | EntryChange::Update{key,..} | EntryChange::Remove{key} => key,
        }
    }

#[getter]
fn new_value(&self) -> Option<PyObject> {
        let gil = Python::acquire_gil();
        let py = gil.python();
        match &self.inner {
            EntryChange::Create{value, ..} => Some(crate::conversions::convert_value(value, &py)),
            EntryChange::Update{new_value, ..} => Some(crate::conversions::convert_value(new_value, &py)),
            EntryChange::Remove{..} => None
        }
}
}

impl DictChange {
    pub fn new(change: EntryChange) -> Self {
        Self{inner: change}
    }

    pub fn creating(key: &str, value: Value) -> Self {
        DictChange{inner: EntryChange::creating(key, value)}
    }
}
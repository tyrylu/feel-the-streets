use crate::entities_query::PyEntitiesQuery;
use crate::entity::PyEntity;
use crate::semantic_change::PySemanticChange;
use osm_db::area_db::AreaDatabase;
use pyo3::exceptions;
use pyo3::prelude::*;

#[pyclass(name=AreaDatabase)]
pub struct PyAreaDatabase {
    inner: AreaDatabase,
}

#[pymethods]
impl PyAreaDatabase {
    #[staticmethod]
    pub fn path_for(osm_id: i64, server_side: bool) -> String {
        AreaDatabase::path_for(osm_id, server_side)
            .to_string_lossy()
            .into_owned()
    }

    #[staticmethod]
    pub fn open_existing(area_osm_id: i64, server_side: bool) -> PyResult<Self> {
        match AreaDatabase::open_existing(area_osm_id, server_side) {
            Ok(db) => Ok(Self { inner: db }),
            Err(e) => Err(exceptions::ValueError::py_err(format!(
                "Failed to open the database, error: {}",
                e
            ))),
        }
    }

    pub fn get_entities(&self, query: &PyEntitiesQuery) -> PyResult<Vec<PyEntity>> {
        match self.inner.get_entities(&query.inner) {
            Ok(res) => Ok(res.into_iter().map(|e| PyEntity { inner: e }).collect()),
            Err(e) => Err(exceptions::ValueError::py_err(format!(
                "Error executing the query: {}",
                e
            ))),
        }
    }
    pub fn get_entities_really_intersecting(
        &self,
        candidate_ids: Vec<&str>,
        x: f64,
        y: f64,
        fast: bool,
    ) -> PyResult<Vec<PyEntity>> {
        match self
            .inner
            .get_entities_really_intersecting(&candidate_ids, x, y, fast)
        {
            Ok(res) => Ok(res.into_iter().map(|e| PyEntity { inner: e }).collect()),
            Err(e) => Err(exceptions::ValueError::py_err(format!(
                "Failed to execute the query, error: {}",
                e
            ))),
        }
    }

    pub fn apply_change(&mut self, change: &PySemanticChange) -> PyResult<()> {
        match self.inner.apply_change(&change.inner) {
            Ok(()) => Ok(()),
            Err(e) => Err(exceptions::ValueError::py_err(format!(
                "Failed to apply the change, error: {}",
                e
            ))),
        }
    }
    pub fn begin(&self) -> PyResult<()> {
        match self.inner.begin() {
            Ok(()) => Ok(()),
            Err(e) => Err(exceptions::ValueError::py_err(format!(
                "Failed to execute BEGIN, error: {}",
                e
            ))),
        }
    }

    pub fn commit(&self) -> PyResult<()> {
        match self.inner.commit() {
            Ok(()) => Ok(()),
            Err(e) => Err(exceptions::ValueError::py_err(format!(
                "Failed to execute COMMIT, error: {}",
                e
            ))),
        }
    }

    pub fn get_entity(&self, osm_id: &str) -> PyResult<Option<PyEntity>> {
        match self.inner.get_entity(osm_id) {
            Ok(res) => Ok(res.map(|e| PyEntity { inner: e })),
            Err(e) => Err(exceptions::ValueError::py_err(format!(
                "Failed to get entity, error: {}",
                e
            ))),
        }
    }

    pub fn get_child_count(&self, parent_id: &str) -> PyResult<u32> {
        match self.inner.get_child_count(parent_id) {
            Ok(num) => Ok(num),
            Err(e) => Err(exceptions::ValueError::py_err(format!("Failed to query child count: {}", e)))
        }
    }
    pub fn get_parent_count(&self, parent_id: &str) -> PyResult<u32> {
        match self.inner.get_parent_count(parent_id) {
            Ok(num) => Ok(num),
            Err(e) => Err(exceptions::ValueError::py_err(format!("Failed to query parent count: {}", e)))
        }
    }
}

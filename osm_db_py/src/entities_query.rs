use crate::field_condition::PyFieldCondition;
use osm_db::entities_query::EntitiesQuery;
use pyo3::prelude::*;

#[pyclass(name=EntitiesQuery)]
pub struct PyEntitiesQuery {
    pub(crate) inner: EntitiesQuery,
}

#[pymethods]
impl PyEntitiesQuery {
    #[new]
    fn new() -> Self {
            PyEntitiesQuery {
                inner: EntitiesQuery::default(),
            }
        
    }

    pub fn set_included_discriminators(&mut self, discriminators: Vec<String>) {
        self.inner.set_included_discriminators(discriminators)
    }

    pub fn set_excluded_discriminators(&mut self, discriminators: Vec<String>) {
        self.inner.set_excluded_discriminators(discriminators)
    }
    pub fn set_rectangle_of_interest(&mut self, min_x: f64, max_x: f64, min_y: f64, max_y: f64) {
        self.inner
            .set_rectangle_of_interest(min_x, max_x, min_y, max_y);
    }

    pub fn add_condition(&mut self, condition: &PyFieldCondition) {
        self.inner.add_condition(condition.inner.clone());
    }

    pub fn set_limit(&mut self, limit: usize) {
        self.inner.set_limit(limit)
    }
}

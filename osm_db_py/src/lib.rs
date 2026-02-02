use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::str::FromStr;

mod area_db;
mod conversions;
mod dict_change;
mod entities_query;
mod entity;
mod entity_metadata;
mod field_condition;
mod field_named;
mod semantic_change;

#[pyclass(eq, eq_int)]
#[derive(PartialEq)]
pub enum ChangeType {
    Create,
    Remove,
    Update,
}

#[pymodule]
mod osm_db {
    use super::*;

    #[pyfunction]
    pub fn all_known_discriminators() -> Vec<&'static String> {
        ::osm_db::entity_metadata::all_known_discriminators()
    }

    #[pyfunction]
    fn init_logging(py: Python, level: &str) -> PyResult<()> {
        let filter = log::LevelFilter::from_str(level).map_err(|e| {
            PyRuntimeError::new_err(format!(
                "Could not parse {level} as a logging level, error: {e}"
            ))
        })?;
        let _handle = pyo3_log::Logger::new(py, pyo3_log::Caching::LoggersAndLevels)
            .map_err(|_| PyRuntimeError::new_err("Logger could not be created"))?
            .filter(filter)
            .install()
            .map_err(|_| {
                PyRuntimeError::new_err("Someone installed a rust-side logger before us")
            })?;
        Ok(())
    }

    #[pymodule_export]
    use super::ChangeType;
    #[pymodule_export]
    use semantic_change::PySemanticChange;
    #[pymodule_export]
    use dict_change::DictChange;
    #[pymodule_export]
    use entity::PyEntity;
    #[pymodule_export]
    use entity_metadata::PyEntityMetadata;
    #[pymodule_export]
    use entity_metadata::PyField;
    #[pymodule_export]
    use entity_metadata::PyEnum;
    #[pymodule_export]
    use entities_query::PyEntitiesQuery;
    #[pymodule_export]
    use field_condition::PyFieldCondition;
    #[pymodule_export]
    use field_named::FieldNamed;
    #[pymodule_export]
    use area_db::PyAreaDatabase;
}

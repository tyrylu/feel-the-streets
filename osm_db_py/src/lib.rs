use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
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

const CHANGE_CREATE: i32 = 0;
const CHANGE_UPDATE: i32 = 1;
const CHANGE_REMOVE: i32 = 2;
const CHANGE_REDOWNLOAD_DATABASE: i32 = 3;

#[pymodule]
fn osm_db(_py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m)]
    pub fn all_known_discriminators() -> Vec<&'static String> {
        osm_db::entity_metadata::all_known_discriminators()
    }

    #[pyfn(m)]
    fn init_logging(py: Python, level: &str) -> PyResult<()> {
        let filter = log::LevelFilter::from_str(&level).map_err(|e| PyRuntimeError::new_err(format!("Could not parse {} as a logging level, error: {}", level, e)))?;
        let _handle = pyo3_log::Logger::new(py, pyo3_log::Caching::LoggersAndLevels).map_err(|_| PyRuntimeError::new_err("Logger could not be created"))?
    .filter(filter)
    .install()
    .map_err(|_| PyRuntimeError::new_err("Someone installed a rust-side logger before us"))?;
    Ok(())
        }

    m.add("CHANGE_CREATE", CHANGE_CREATE)?;
    m.add("CHANGE_UPDATE", CHANGE_UPDATE)?;
    m.add("CHANGE_REMOVE", CHANGE_REMOVE)?;
    m.add("CHANGE_REDOWNLOAD_DATABASE", CHANGE_REDOWNLOAD_DATABASE)?;
    m.add_class::<semantic_change::PySemanticChange>()?;
    m.add_class::<dict_change::DictChange>()?;
    m.add_class::<entity::PyEntity>()?;
    m.add_class::<entity_metadata::PyEntityMetadata>()?;
    m.add_class::<entity_metadata::PyField>()?;
    m.add_class::<entity_metadata::PyEnum>()?;
    m.add_class::<entities_query::PyEntitiesQuery>()?;
    m.add_class::<field_condition::PyFieldCondition>()?;
    m.add_class::<field_named::FieldNamed>()?;
    m.add_class::<area_db::PyAreaDatabase>()?;
    Ok(())
}

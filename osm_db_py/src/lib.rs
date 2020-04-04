use pyo3::prelude::*;

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

#[pymodule]
fn osm_db(_py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m, "all_known_discriminators")]
    pub fn all_known_discriminators() -> Vec<&'static String> {
        osm_db::entity_metadata::all_known_discriminators()
    }

    #[pyfn(m, "init_logging")]
    fn init_logging() {
        env_logger::Builder::from_env("FTS_LOG")
            .format_timestamp(None)
            .init();
    }

    m.add("CHANGE_CREATE", CHANGE_CREATE)?;
    m.add("CHANGE_UPDATE", CHANGE_UPDATE)?;
    m.add("CHANGE_REMOVE", CHANGE_REMOVE)?;
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

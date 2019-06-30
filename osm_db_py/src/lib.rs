use pyo3::prelude::*;

mod semantic_change;
mod dict_change;
mod conversions;

const CHANGE_CREATE: i32 = 0;
const CHANGE_UPDATE: i32 = 1;
const CHANGE_REMOVE: i32 = 2;

#[pymodule]
fn osm_db(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add("CHANGE_CREATE", CHANGE_CREATE)?;
        m.add("CHANGE_UPDATE", CHANGE_UPDATE)?;
        m.add("CHANGE_REMOVE", CHANGE_REMOVE)?;
        m.add_class::<semantic_change::PySemanticChange>()?;
        m.add_class::<dict_change::DictChange>()?;
    Ok(())
}
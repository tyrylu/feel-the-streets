use pyo3::prelude::*;

mod semantic_change;


#[pymodule]
fn osm_db(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<semantic_change::PySemanticChange>()?;
    Ok(())
}
use osm_db::semantic_change::SemanticChange;
use pyo3::prelude::*;
use pyo3::exceptions;

#[pyclass(name=SemanticChange)]
pub struct PySemanticChange {
    inner: SemanticChange
}

#[pymethods]
impl PySemanticChange {
    #[staticmethod]
    fn from_json(json: &str) -> PyResult<Py<PySemanticChange>> {
    match serde_json::from_str::<SemanticChange>(json) {
        Ok(change) => {
                let gil = Python ::acquire_gil();
    let py = gil.python();
    Ok(Py::new(py, PySemanticChange {inner: change}).unwrap())
        },
        Err(e) => Err(exceptions::ValueError::py_err(format!("Could not parse json, error: {}", e)))
    }
    }
}
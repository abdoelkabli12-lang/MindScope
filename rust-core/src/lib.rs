use pyo3::prelude::*;

pub mod config;
pub mod ingestion;
pub mod analysis;
pub mod duplicates;
pub mod validation;

#[pymodule]
fn mindscope_core(m: &Bound<'_, PyModule>) -> PyResult<()> {

    // Ingestion
    m.add_function(wrap_pyfunction!(ingestion::py_ingest_dataset, m)?)?;
    m.add_function(wrap_pyfunction!(ingestion::py_validate_record_length, m)?)?;

    // Analysis
    m.add_function(wrap_pyfunction!(analysis::py_analyze_missing_values, m)?)?;

    // Duplicate detection and handling
    m.add_function(wrap_pyfunction!(duplicates::py_detect_duplicate_ids, m)?)?;
    m.add_function(wrap_pyfunction!(duplicates::py_report_duplicate_records, m)?)?;
    m.add_function(wrap_pyfunction!(duplicates::py_remove_duplicate_ids, m)?)?;

    // Validation
    m.add_function(wrap_pyfunction!(validation::py_validate_categorical_values, m)?)?;
    m.add_function(wrap_pyfunction!(validation::py_validate_numerical_values, m)?)?;

    Ok(())
}
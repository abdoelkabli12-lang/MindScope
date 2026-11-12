use std::{collections::HashMap, error::Error};
use csv::StringRecord;
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

// Original Rust function
pub fn analyze_missing_values<'a>(
    headers: &'a StringRecord,
    records: &[&StringRecord],
) -> Result<HashMap<&'a str, usize>, Box<dyn Error>> {
    let mut missing_cols: HashMap<&str, usize> = HashMap::new();

    for record in records {
        for (index, field) in record.iter().enumerate() {
            let col = headers.get(index).ok_or("Not a field")?;

            if field.trim().is_empty() {
                *missing_cols.entry(col).or_insert(0) += 1;
            }
        }
    }

    Ok(missing_cols)
}

// Python wrapper
#[pyfunction(name = "analyze_missing_values")]
pub fn py_analyze_missing_values(
    headers: Vec<String>,
    records: Vec<Vec<String>>,
) -> PyResult<HashMap<String, usize>> {

    let mut missing_cols: HashMap<String, usize> = HashMap::new();

    for record in &records {
        for (index, field) in record.iter().enumerate() {
            let col = headers
                .get(index)
                .ok_or_else(|| PyValueError::new_err("Record contains an unexpected field"))?;

            if field.trim().is_empty() {
                *missing_cols.entry(col.clone()).or_insert(0) += 1;
            }
        }
    }

    Ok(missing_cols)
}
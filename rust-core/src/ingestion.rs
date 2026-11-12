use csv::{Reader, StringRecord};
use std::{error::Error, fs::File};
use pyo3::{
    prelude::*,
    exceptions::{PyValueError},
};
use crate::config::COLUMN_NAMES;

// Original Rust function — used by main.rs
pub fn ingest_dataset(
    filepath: &str,
) -> Result<(Vec<StringRecord>, StringRecord), Box<dyn Error>> {
    let file = File::open(filepath)?;
    let mut rdr = Reader::from_reader(file);

    let headers = rdr.headers()?.clone();

    for result in &headers {
        if !COLUMN_NAMES.contains(&result) {
            println!("Column not found in the default list: {}", result);
        }
    }

    for column in COLUMN_NAMES {
        if !headers.iter().any(|header| header == column) {
            println!("Missing Column: {}", column);
        }
    }

    if headers.len() != COLUMN_NAMES.len() {
        println!("Insufficient number of columns");
    }

    let records_vec: Vec<StringRecord> =
        rdr.records().collect::<Result<Vec<_>, csv::Error>>()?;

    Ok((records_vec, headers))
}

// Python wrapper
#[pyfunction(name = "ingest_dataset")]
pub fn py_ingest_dataset(
    filepath: &str,
) -> PyResult<(Vec<Vec<String>>, Vec<String>)> {
    let (records, headers) = ingest_dataset(filepath)
        .map_err(|e| {
            PyValueError::new_err(e.to_string())
        })?;

    let records_vec: Vec<Vec<String>> = records
        .iter()
        .map(|record| {
            record.iter().map(|field| field.to_string()).collect()
        })
        .collect();

    let headers_vec: Vec<String> = headers
        .iter()
        .map(|field| field.to_string())
        .collect();

    Ok((records_vec, headers_vec))
}

// Original Rust function — used by main.rs
pub fn validate_record_length(
    records: &[StringRecord],
) -> Result<(usize, usize), Box<dyn Error>> {
    let mut valid_records = 0;
    let mut invalid_records = 0;

    for record in records {
        if record.len() != COLUMN_NAMES.len() {
            invalid_records += 1;
        } else {
            valid_records += 1;
        }
    }

    Ok((valid_records, invalid_records))
}

// Python wrapper
#[pyfunction(name = "validate_record_length")]
pub fn py_validate_record_length(
    records: Vec<Vec<String>>,
) -> (usize, usize) {
    let mut valid_records = 0;
    let mut invalid_records = 0;

    for record in &records {
        if record.len() != COLUMN_NAMES.len() {
            invalid_records += 1;
        } else {
            valid_records += 1;
        }
    }

    (valid_records, invalid_records)
}
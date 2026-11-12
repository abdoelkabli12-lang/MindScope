use std::collections::{HashMap, HashSet};
use std::error::Error;

use csv::StringRecord;
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;


// ============================================================
// Original Rust functions
// ============================================================

pub fn detect_duplicate_ids<'a>(
    headers: &StringRecord,
    records: &'a [StringRecord],
) -> Result<HashMap<&'a str, usize>, Box<dyn Error>> {

    let id_pos = headers
        .iter()
        .position(|id| id == "Student_ID")
        .ok_or("No ID column found")?;

    let mut counts: HashMap<&str, usize> = HashMap::new();

    for (ind, record) in records.iter().enumerate() {
        let student_id = record.get(id_pos).ok_or("No ID was found")?;

        if student_id.is_empty() {
            println!("The ID for record {} is empty", ind + 1);
            continue;
        }

        *counts.entry(student_id).or_insert(0) += 1;
    }

    Ok(counts)
}


pub fn report_duplicate_records(
    headers: &StringRecord,
    records: &[StringRecord],
    map: &HashMap<&str, usize>,
) -> Result<(), Box<dyn Error>> {

    let id_pos = headers
        .iter()
        .position(|id| id == "Student_ID")
        .ok_or("No ID found")?;

    for (ind, record) in records.iter().enumerate() {
        let student_id = record.get(id_pos).ok_or("No ID found")?;

        if student_id.is_empty() {
            println!("The ID for record {} is empty", ind + 1);
            continue;
        }

        let map_id_occurrence = map
            .get(student_id)
            .ok_or("ID was not found in map")?;

        if *map_id_occurrence > 1 {
            println!("Duplicate record {}:", ind + 1);
            println!("{:?}", record);
        }
    }

    Ok(())
}


pub fn remove_duplicate_ids<'a>(
    headers: &StringRecord,
    records: &'a [StringRecord],
) -> Result<Vec<&'a StringRecord>, Box<dyn Error>> {

    let mut id_set: HashSet<&str> = HashSet::new();
    let mut rec_vec: Vec<&StringRecord> = Vec::new();

    let id_pos = headers
        .iter()
        .position(|id| id == "Student_ID")
        .ok_or("No ID found")?;

    for (ind, record) in records.iter().enumerate() {
        let student_id = record.get(id_pos).ok_or("No ID found")?;

        if student_id.is_empty() {
            println!("The ID for record {} is empty", ind + 1);
            continue;
        }

        if id_set.insert(student_id) {
            rec_vec.push(record);
        }
    }

    Ok(rec_vec)
}


// ============================================================
// Python wrappers
// ============================================================

#[pyfunction(name = "detect_duplicate_ids")]
pub fn py_detect_duplicate_ids(
    headers: Vec<String>,
    records: Vec<Vec<String>>,
) -> PyResult<HashMap<String, usize>> {

    let id_pos = headers
        .iter()
        .position(|id| id == "Student_ID")
        .ok_or_else(|| PyValueError::new_err("No ID column found"))?;

    let mut counts: HashMap<String, usize> = HashMap::new();

    for (ind, record) in records.iter().enumerate() {
        let student_id = record
            .get(id_pos)
            .ok_or_else(|| PyValueError::new_err("No ID was found"))?;

        if student_id.trim().is_empty() {
            println!("The ID for record {} is empty", ind + 1);
            continue;
        }

        *counts.entry(student_id.clone()).or_insert(0) += 1;
    }

    Ok(counts)
}


#[pyfunction(name = "report_duplicate_records")]
pub fn py_report_duplicate_records(
    headers: Vec<String>,
    records: Vec<Vec<String>>,
    map: HashMap<String, usize>,
) -> PyResult<()> {

    let id_pos = headers
        .iter()
        .position(|id| id == "Student_ID")
        .ok_or_else(|| PyValueError::new_err("No ID column found"))?;

    for (ind, record) in records.iter().enumerate() {
        let student_id = record
            .get(id_pos)
            .ok_or_else(|| PyValueError::new_err("No ID was found"))?;

        if student_id.trim().is_empty() {
            println!("The ID for record {} is empty", ind + 1);
            continue;
        }

        let occurrence = map
            .get(student_id)
            .ok_or_else(|| PyValueError::new_err("ID was not found in map"))?;

        if *occurrence > 1 {
            println!("Duplicate record {}:", ind + 1);
            println!("{:?}", record);
        }
    }

    Ok(())
}


#[pyfunction(name = "remove_duplicate_ids")]
pub fn py_remove_duplicate_ids(
    headers: Vec<String>,
    records: Vec<Vec<String>>,
) -> PyResult<Vec<Vec<String>>> {

    let id_pos = headers
        .iter()
        .position(|id| id == "Student_ID")
        .ok_or_else(|| PyValueError::new_err("No ID column found"))?;

    let mut id_set: HashSet<String> = HashSet::new();
    let mut rec_vec: Vec<Vec<String>> = Vec::new();

    for (ind, record) in records.into_iter().enumerate() {
        let student_id = record
            .get(id_pos)
            .ok_or_else(|| PyValueError::new_err("No ID was found"))?;

        if student_id.trim().is_empty() {
            println!("The ID for record {} is empty", ind + 1);
            continue;
        }

        if id_set.insert(student_id.clone()) {
            rec_vec.push(record);
        }
    }

    Ok(rec_vec)
}
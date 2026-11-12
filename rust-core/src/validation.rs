use std::error::Error;
use csv::StringRecord;

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

use crate::config::{
    DIET_QUALITY_CATEGORIES,
    GENDER_CATEGORIES,
    MENTAL_HEALTH_HISTORY_CATEGORIES,
    MENTAL_HEALTH_RISK_CATEGORIE,
    PART_TIME_JOB_CATEGORIES,
    PHYSICAL_ACTIVITY_CATEGORIES,
    YEAR_OF_STUDY,
    NUMERICAL_COLUMNS,
};

// ============================================================
// Original Rust function: Categorical validation
// ============================================================

pub fn validate_categorical_values(
    headers: &StringRecord,
    records: &[&StringRecord],
) -> Result<(), Box<dyn Error>> {

    let categories: Vec<(&str, &[&str])> = vec![
        ("Gender", &GENDER_CATEGORIES),
        ("Physical_Activity", &PHYSICAL_ACTIVITY_CATEGORIES),
        ("Diet_Quality", &DIET_QUALITY_CATEGORIES),
        ("Part_Time_Job", &PART_TIME_JOB_CATEGORIES),
        ("Previous_Mental_Health_History", &MENTAL_HEALTH_HISTORY_CATEGORIES),
        ("Mental_Health_Risk", &MENTAL_HEALTH_RISK_CATEGORIE),
        ("Year_of_Study", &YEAR_OF_STUDY),
    ];

    let mut valid_count = 0;
    let mut invalid_count = 0;

    for (column, allowed_val) in categories {
        let col_index = headers
            .iter()
            .position(|c| c == column)
            .ok_or("Column not found")?;

        for (ind, record) in records.iter().enumerate() {
            let field = record.get(col_index).ok_or("Field not found")?;

            if field.trim().is_empty() {
                println!(
                    "Empty value in column {} at record {}",
                    column,
                    ind + 1
                );
                continue;
            }

            if allowed_val.contains(&field.trim()) {
                valid_count += 1;
            } else {
                println!(
                    "Field {:?} in record {} has an invalid value in {}",
                    field,
                    ind + 1,
                    column
                );
                invalid_count += 1;
            }
        }
    }

    println!("Valid values count: {}", valid_count);
    println!("Invalid values count: {}", invalid_count);

    if invalid_count > 0 {
        Err(format!(
            "Validation failed: {} invalid value(s) found",
            invalid_count
        ).into())
    } else {
        Ok(())
    }
}

// ============================================================
// Original Rust function: Numerical validation
// ============================================================

pub fn validate_numerical_values(
    headers: &StringRecord,
    records: &[&StringRecord],
) -> Result<(), Box<dyn Error>> {

    let mut valid_count = 0;
    let mut invalid_count = 0;

    for column in NUMERICAL_COLUMNS {
        let col_index = headers
            .iter()
            .position(|c| c == column)
            .ok_or("Column not found")?;

        for (ind, record) in records.iter().enumerate() {
            let field = record.get(col_index).ok_or("Field not found")?;

            if field.trim().is_empty() {
                println!(
                    "Missing value in {} at record {}",
                    column,
                    ind + 1
                );
                continue;
            }

            match field.trim().parse::<f64>() {
                Ok(_) => valid_count += 1,
                Err(_) => invalid_count += 1,
            }
        }
    }

    println!("Valid values: {}", valid_count);
    println!("Invalid values: {}", invalid_count);

    if invalid_count > 0 {
        Err(format!(
            "Validation failed: {} invalid value(s)",
            invalid_count
        ).into())
    } else {
        Ok(())
    }
}

// ============================================================
// Python wrapper: Categorical validation
// ============================================================

#[pyfunction(name = "validate_categorical_values")]
pub fn py_validate_categorical_values(
    headers: Vec<String>,
    records: Vec<Vec<String>>,
) -> PyResult<()> {

    let categories: Vec<(&str, &[&str])> = vec![
        ("Gender", &GENDER_CATEGORIES),
        ("Physical_Activity", &PHYSICAL_ACTIVITY_CATEGORIES),
        ("Diet_Quality", &DIET_QUALITY_CATEGORIES),
        ("Part_Time_Job", &PART_TIME_JOB_CATEGORIES),
        ("Previous_Mental_Health_History", &MENTAL_HEALTH_HISTORY_CATEGORIES),
        ("Mental_Health_Risk", &MENTAL_HEALTH_RISK_CATEGORIE),
        ("Year_of_Study", &YEAR_OF_STUDY),
    ];

    let mut valid_count = 0;
    let mut invalid_count = 0;

    for (column, allowed_val) in categories {
        let col_index = headers
            .iter()
            .position(|c| c == column)
            .ok_or_else(|| PyValueError::new_err(
                format!("Column {} not found", column)
            ))?;

        for (ind, record) in records.iter().enumerate() {
            let field = record
                .get(col_index)
                .ok_or_else(|| PyValueError::new_err("Field not found"))?;

            if field.trim().is_empty() {
                println!(
                    "Empty value in column {} at record {}",
                    column,
                    ind + 1
                );
                continue;
            }

            if allowed_val.contains(&field.trim()) {
                valid_count += 1;
            } else {
                println!(
                    "Invalid value {:?} in column {} at record {}",
                    field,
                    column,
                    ind + 1
                );
                invalid_count += 1;
            }
        }
    }

    println!("Valid values count: {}", valid_count);
    println!("Invalid values count: {}", invalid_count);

    if invalid_count > 0 {
        return Err(PyValueError::new_err(
            format!(
                "Validation failed: {} invalid value(s)",
                invalid_count
            )
        ));
    }

    Ok(())
}

// ============================================================
// Python wrapper: Numerical validation
// ============================================================

#[pyfunction(name = "validate_numerical_values")]
pub fn py_validate_numerical_values(
    headers: Vec<String>,
    records: Vec<Vec<String>>,
) -> PyResult<()> {

    let mut valid_count = 0;
    let mut invalid_count = 0;

    for column in NUMERICAL_COLUMNS {
        let col_index = headers
            .iter()
            .position(|c| c == column)
            .ok_or_else(|| PyValueError::new_err(
                format!("Column {} not found", column)
            ))?;

        for (ind, record) in records.iter().enumerate() {
            let field = record
                .get(col_index)
                .ok_or_else(|| PyValueError::new_err("Field not found"))?;

            if field.trim().is_empty() {
                println!(
                    "Missing value in {} at record {}",
                    column,
                    ind + 1
                );
                continue;
            }

            match field.trim().parse::<f64>() {
                Ok(_) => valid_count += 1,
                Err(_) => {
                    println!(
                        "Invalid numerical value in {} at record {}",
                        column,
                        ind + 1
                    );
                    invalid_count += 1;
                }
            }
        }
    }

    println!("Valid values: {}", valid_count);
    println!("Invalid values: {}", invalid_count);

    if invalid_count > 0 {
        return Err(PyValueError::new_err(
            format!(
                "Validation failed: {} invalid value(s)",
                invalid_count
            )
        ));
    }

    Ok(())
}
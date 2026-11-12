use std::error::Error;
use csv::{StringRecord};
use crate::config::{DIET_QUALITY_CATEGORIES, GENDER_CATEGORIES, MENTAL_HEALTH_HISTORY_CATEGORIES, MENTAL_HEALTH_RISK_CATEGORIE, PART_TIME_JOB_CATEGORIES, PHYSICAL_ACTIVITY_CATEGORIES, YEAR_OF_STUDY, NUMERICAL_COLUMNS};


pub fn validate_categorical_values(headers: &StringRecord, records: &[&StringRecord]) -> Result<(), Box<dyn Error>> {
  let categories: Vec<(&str, &[&str])> = vec!(
    ("Gender", &GENDER_CATEGORIES),
    ("Physical_Activity", &PHYSICAL_ACTIVITY_CATEGORIES),
    ("Diet_Quality", &DIET_QUALITY_CATEGORIES),
    ("Part_Time_Job", &PART_TIME_JOB_CATEGORIES),
    ("Previous_Mental_Health_History", &MENTAL_HEALTH_HISTORY_CATEGORIES),
    ("Mental_Health_Risk", &MENTAL_HEALTH_RISK_CATEGORIE),
    ("Year_of_Study", &YEAR_OF_STUDY)
  );
  let mut valid_count = 0;
  let mut invalid_count = 0;

  for (column, allowed_val) in categories {
    let col_index = headers.iter().position(|c| c == column).ok_or("Not Found")?;
    for(ind, record) in records.iter().enumerate(){
      let field = record.get(col_index).ok_or("Not Found")?;
      if field.trim().is_empty() {
        println!("The value for the column field {} is empty in the record {}", column, ind + 1);
        continue;
    }
    if allowed_val.contains(&field.trim()){
      valid_count += 1;
    } else {
      println!("filed {:#?} index of record {} has an invalid value in {} column", field, ind + 1, column);
      invalid_count += 1;
    }
    }
  }

  println!("Valid values count {}\n", valid_count);
  println!("Invalid values count {}", invalid_count);
  if invalid_count > 0 {
    Err(format!("Validation failed: {} invalid value(s) found", invalid_count).into())
} else {
    Ok(())
}
}

pub fn validate_numerical_values(
    headers: &StringRecord,
    records: &[&StringRecord]
) -> Result<(), Box<dyn Error>> {

    let mut valid_count = 0;
    let mut invalid_count = 0;

    for column in NUMERICAL_COLUMNS {
        let col_index = headers.iter().position(|c| c == column).ok_or("Column not found")?;
        for (ind, record) in records.iter().enumerate() {
            let field = record.get(col_index).ok_or("Field not found")?;
            if field.trim().is_empty() {
                println!("Missing value in {} at record {}", column, ind + 1);
                continue;
            }

            match field.parse::<f64>() {
              Ok(_) => valid_count += 1,
              Err(_) => invalid_count += 1,
            }
        }
    }

    println!("Valid values: {}", valid_count);
    println!("Invalid values: {}", invalid_count);

    if invalid_count > 0 {
        Err(format!("Validation failed: {} invalid value(s)", invalid_count).into())
    } else {
        Ok(())
    }
}
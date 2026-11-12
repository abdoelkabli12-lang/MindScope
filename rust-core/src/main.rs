mod config;
mod ingestion;
mod analysis;
mod validation;
mod duplicates;

use crate::{duplicates::{detect_duplicate_ids, remove_duplicate_ids, report_duplicate_records},
          ingestion::{ingest_dataset, validate_record_length}, 
          validation::{validate_categorical_values, validate_numerical_values}, 
          analysis::analyze_missing_values};

use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let (records, headers) = ingest_dataset("../../data/raw/student_mental_health.csv")?;
    let (valid, invalid) = validate_record_length(&records)?;
    println!("Valid records: {} \nInvalid records: {}", valid, invalid);
    if invalid > 0 {
      return Err(format!("Validation failed: {} invalid record(s) found", invalid).into())
    }
    let dup_detect = detect_duplicate_ids(&headers, &records)?;
    // print!("{:?}", dup_detect);
    let dup_report = report_duplicate_records(&headers, &records, &dup_detect);
    print!("{:?}", dup_report);
    let delete_dups = remove_duplicate_ids(&headers, &records)?;
    print!("{:?}", delete_dups);

    
    let miss_val_rep = analyze_missing_values(&headers, &delete_dups)?; 
    for (missing, count) in miss_val_rep{
      let percentage = (count as f64) / (delete_dups.len() as f64) * 100.0;
      println!("\n\ncolumn: {} \nmissing count: {} \n", missing, count);
      println!("The percentage: {}%", percentage);
    }
    let cat_val = validate_categorical_values(&headers, &delete_dups)?;
    println!("{:#?}", cat_val);
    let num_val = validate_numerical_values(&headers, &delete_dups)?;
    println!("{:#?}", num_val);


    Ok(())
}










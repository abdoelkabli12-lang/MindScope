mod config;

use std::{collections::{HashMap, HashSet}, error::Error};
use csv::{Reader, StringRecord};
use crate::config::{COLUMN_NAMES};
use std::fs::File;

fn main() -> Result<(), Box<dyn Error>> {
    let (records, headers) = ingest_dataset("../../data/raw/student_mental_health.csv")?;
    let (valid, invalid) = validate_record_length(&records)?;
    println!("Valid records: {} \nInvalid records: {}", valid, invalid);
    let dup_detect = detect_duplicate_ids(&headers, &records)?;
    // print!("{:?}", dup_detect);
    let dup_report = report_duplicate_records(&headers, &records, &dup_detect);
    print!("{:?}", dup_report);
    let delete_dups = remove_duplicate_ids(&headers, &records);
    print!("{:?}", delete_dups);

    let miss_val_rep = analyze_missing_values(&headers, &records)?; 
    for (missing, count) in miss_val_rep{
      let percentage = (count as f64) / (records.len() as f64) * 100.0;
      println!("\n\ncolumn: {} \nmissing count: {} \n", missing, count);
      println!("The percentage: {}%", percentage);
    }

    Ok(())
}



fn ingest_dataset(filepath: &str) -> Result<(Vec<StringRecord>, StringRecord), Box<dyn Error>> {
  let file = File::open(filepath)?;
  let mut rdr = Reader::from_reader(file);
  let headers = rdr.headers()?.clone();
  for result in &headers{
    if !COLUMN_NAMES.contains(&result) {
        println!("Column not found in the default list {}", result);
    }
    }
      for column in COLUMN_NAMES{
        if !headers.iter().any(|header| header == column) {
            println!("Missing Column {}", column);
        }
    }
    if headers.len() != COLUMN_NAMES.len() {
        println!("Insufficient number of columns");
    }

  let records_vec: Vec<StringRecord> = rdr.records().collect::<Result<Vec<StringRecord>, csv::Error>>()?;


  Ok((records_vec, headers))

}

fn validate_record_length(records: &[StringRecord]) -> Result<(usize, usize), Box<dyn Error>> {
  let mut valid_records : usize = 0;
  let mut invalid_records: usize = 0;
  for record in records {
    if record.len() != COLUMN_NAMES.len() {
      invalid_records += 1;
    } else {
      valid_records += 1;
    }
  }
  Ok((valid_records, invalid_records))
}

fn detect_duplicate_ids<'a>(headers: &StringRecord, records: &'a[StringRecord]) -> Result<HashMap<&'a str, usize>, Box<dyn Error>> {
  let id_pos = headers.iter().position(|id| id == "Student_ID");
  let mut counts: HashMap<&str, usize> = HashMap::new();
  let id = id_pos.ok_or("No Id column found")?;
  for (ind, record) in records.iter().enumerate(){
    let student_id = record.get(id);
    let student_id = student_id.ok_or("No Id was found")?;
    if student_id.is_empty() {
        println!("The ID for the record {} is empty", ind);
        continue;
    }
    *counts.entry(student_id).or_insert(0) += 1;
  }

  Ok(counts)
}

fn report_duplicate_records (headers: &StringRecord, records: &[StringRecord], map: &HashMap<&str, usize>) -> Result<(), Box<dyn Error>> {
  let id_pos = headers.iter().position(|id| id == "Student_ID").ok_or("No Id found")?;

  for (ind, record) in records.iter().enumerate() {
    let student_id = record.get(id_pos).ok_or("No Id Found")?;
    if student_id.is_empty() {
        println!("The ID for the record {} is empty", ind + 1);
        continue;
    }
    let map_id_occurence = map.get(&student_id).ok_or("No Id Was Found")?;

    if *map_id_occurence > 1 {
      println!("invalid records : \n");
      println!("{:?}", record);
    }
  }
  Ok(())
}

fn remove_duplicate_ids <'a>(headers: &StringRecord, records: &'a[StringRecord]) -> Result<Vec<&'a StringRecord>, Box<dyn Error>> {
  let mut id_set: HashSet<&str> = HashSet::new();
  let mut rec_vec: Vec<&StringRecord> = Vec::new();
  let id_pos = headers.iter().position(|id| id == "Student_ID").ok_or("No Id found")?;


  for (ind, record) in records.iter().enumerate() {
    let student_id = record.get(id_pos).ok_or("No Id Found")?;
    if student_id.is_empty() {
        println!("The ID for the record {} is empty", ind + 1);
        continue;
    }
    if id_set.insert(student_id) {
      rec_vec.push(record);
    } else {
      continue;
    }
  }
  Ok(rec_vec)
}

fn analyze_missing_values <'a>(headers: &'a StringRecord, records: &[StringRecord]) -> Result<HashMap<&'a str, usize> ,Box<dyn Error>> {
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
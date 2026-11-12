use std::error::Error;
use csv::{Reader, StringRecord};
use crate::config::{COLUMN_NAMES};
use std::fs::File;


pub fn ingest_dataset(filepath: &str) -> Result<(Vec<StringRecord>, StringRecord), Box<dyn Error>> {
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

pub fn validate_record_length(records: &[StringRecord]) -> Result<(usize, usize), Box<dyn Error>> {
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
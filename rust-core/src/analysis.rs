use std::{collections::{HashMap}, error::Error};
use csv::{StringRecord};


pub fn analyze_missing_values <'a>(headers: &'a StringRecord, records: &[&StringRecord]) -> Result<HashMap<&'a str, usize> ,Box<dyn Error>> {
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
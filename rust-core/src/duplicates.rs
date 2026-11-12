use std::{collections::{HashMap, HashSet}, error::Error};
use csv::{StringRecord};


pub fn detect_duplicate_ids<'a>(headers: &StringRecord, records: &'a[StringRecord]) -> Result<HashMap<&'a str, usize>, Box<dyn Error>> {
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

pub fn report_duplicate_records (headers: &StringRecord, records: &[StringRecord], map: &HashMap<&str, usize>) -> Result<(), Box<dyn Error>> {
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

pub fn remove_duplicate_ids <'a>(headers: &StringRecord, records: &'a[StringRecord]) -> Result<Vec<&'a StringRecord>, Box<dyn Error>> {
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
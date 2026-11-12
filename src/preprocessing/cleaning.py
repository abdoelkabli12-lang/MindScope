import mindscope_core as ms
import pandas as pd


DATA_PATH = "data/raw/student_mental_health.csv"

records, headers = ms.ingest_dataset(DATA_PATH)

print("\n========== DATASET OVERVIEW ==========")
print(f"Records : {len(records)}")
print(f"Columns : {len(headers)}")

valid, invalid = ms.validate_record_length(records)

print("\n========== STRUCTURAL VALIDATION ==========")
print(f"Valid records   : {valid}")
print(f"Invalid records : {invalid}")

dup_ids = ms.detect_duplicate_ids(headers, records)

print("\n========== DUPLICATE ANALYSIS ==========")

if dup_ids:
    ms.report_duplicate_records(headers, records, dup_ids)
else:
    print("No duplicate IDs found.")

clean_records = ms.remove_duplicate_ids(headers, records)

print(f"\nRecords before removal : {len(records)}")
print(f"Records after removal  : {len(clean_records)}")
print(f"Records removed        : {len(records) - len(clean_records)}")

print("\n========== DATA VALIDATION ==========")

ms.validate_categorical_values(headers, clean_records)
print("Categorical validation : PASSED")

ms.validate_numerical_values(headers, clean_records)
print("Numerical validation   : PASSED")

missing_vals = ms.analyze_missing_values(headers, clean_records)

missing_df = pd.DataFrame(
    missing_vals.items(),
    columns=["Feature", "Missing_Count"]
)

missing_df["Missing_Percentage"] = (
    missing_df["Missing_Count"] / len(clean_records) * 100
)

missing_df = (
    missing_df
    .sort_values("Missing_Count", ascending=False)
    .reset_index(drop=True)
)

print("\n========== MISSING VALUES REPORT ==========")
print(missing_df.to_string(
    index=False,
    formatters={"Missing_Percentage": "{:.2f}%".format}
))

print(f"\nTotal missing values : {missing_df['Missing_Count'].sum()}")
print(f"Features affected    : {len(missing_df)}")
import mindscope_core as ms
import pandas as pd

from pathlib import Path


DATA_PATH = "data/raw/student_mental_health.csv"
PROCESSED_PATH = Path("data/processed/cleaned_dataset.csv")


def clean_dataset(verbose=True):
    records, headers = ms.ingest_dataset(DATA_PATH)

    if verbose:
        print("\n========== DATASET OVERVIEW ==========")
        print(f"Records : {len(records)}")
        print(f"Columns : {len(headers)}")

    valid, invalid = ms.validate_record_length(records)

    if verbose:
        print("\n========== STRUCTURAL VALIDATION ==========")
        print(f"Valid records   : {valid}")
        print(f"Invalid records : {invalid}")

    if invalid:
        raise ValueError(f"Dataset contains {invalid} structurally invalid records.")

    dup_ids = ms.detect_duplicate_ids(headers, records)

    if verbose:
        print("\n========== DUPLICATE ANALYSIS ==========")

        if dup_ids:
            ms.report_duplicate_records(headers, records, dup_ids)
        else:
            print("No duplicate IDs found.")

    clean_records = ms.remove_duplicate_ids(headers, records)

    if verbose:
        print(f"\nRecords before removal : {len(records)}")
        print(f"Records after removal  : {len(clean_records)}")
        print(f"Records removed        : {len(records) - len(clean_records)}")

    ms.validate_categorical_values(headers, clean_records)
    ms.validate_numerical_values(headers, clean_records)

    if verbose:
        print("\n========== DATA VALIDATION ==========")
        print("Categorical validation : PASSED")
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

    if verbose:
        print("\n========== MISSING VALUES REPORT ==========")
        print(missing_df.to_string(
            index=False,
            formatters={"Missing_Percentage": "{:.2f}%".format}
        ))

        print(f"\nTotal missing values : {missing_df['Missing_Count'].sum()}")
        print(f"Features affected    : {len(missing_df)}")

    df = pd.DataFrame(clean_records, columns=headers)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)

    if verbose:
        print(f"\nCleaned dataset saved to: {PROCESSED_PATH}")

    return df

clean_dataset()
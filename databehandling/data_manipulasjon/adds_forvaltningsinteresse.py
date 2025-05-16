import pandas as pd
from pathlib import Path


##### Configuration #####
# Column name for scientific name IDs in the Excel file (fra Metadata).
EXCEL_ID_COL = "ValidScientificNameId"
# Column name for scientific name IDs in the input CSV file.
CSV_ID_COL = "validScientificNameId"
# Column name for scientific rank in the input CSV file.
CSV_RANK_COL = "scientificNameRank"
# 0-based index (5th col) in Excel where criteria cols start.
# Adjust if Excel layout changes.
CRITERIA_START_COL_INDEX = 4

##### Main Logic #####


## Function: add_forvaltning_columns ##
def add_forvaltning_columns(
    cleaned_csv_path,  # Input CSV path.
    excel_path,  # Input Excel path.
    output_path,  # Output CSV path.
):
    # --- Load data (Happy Path Only) ---
    df_excel = pd.read_excel(excel_path)
    df_csv_cleaned = pd.read_csv(cleaned_csv_path, sep=";")

    # --- Identify and Prepare Criteria Columns from Excel ---
    potential_criteria_cols = df_excel.columns[CRITERIA_START_COL_INDEX:]
    criteria_cols = [col for col in potential_criteria_cols if col.startswith("Kriterium")]

    # Ensure EXCEL_ID_COL exists
    if EXCEL_ID_COL not in df_excel.columns:
        raise ValueError(f"Excel ID column '{EXCEL_ID_COL}' not found in Excel file.")

    df_excel_indexed = df_excel.set_index(EXCEL_ID_COL)

    df_criteria_bool = pd.DataFrame(index=df_excel_indexed.index)
    for col in criteria_cols:
        if col in df_excel_indexed.columns:
            is_x = df_excel_indexed[col].astype(str).str.strip().str.upper()
            df_criteria_bool[col] = is_x.eq("X").map({True: "Yes", False: "No"})
        else:
            # If a Kriterium col is expected but missing, fill with No for all species in Excel
            df_criteria_bool[col] = "No"

    # --- Validate required columns in df_csv_cleaned ---
    if CSV_RANK_COL not in df_csv_cleaned.columns:
        raise ValueError(f"CSV rank column '{CSV_RANK_COL}' not found in cleaned CSV file.")
    if CSV_ID_COL not in df_csv_cleaned.columns:
        raise ValueError(f"CSV ID column '{CSV_ID_COL}' not found in cleaned CSV file.")

    # --- Merge ALL CSV data with Excel criteria ---
    # All rows from df_csv_cleaned are kept.
    # If a match on CSV_ID_COL and df_criteria_bool.index occurs, criteria are merged.
    # Otherwise, columns from df_criteria_bool will be NaN for that row.
    df_processing = pd.merge(
        df_csv_cleaned,
        df_criteria_bool,
        left_on=CSV_ID_COL,
        right_index=True,
        how="left",
        indicator=True,  # To identify match status
    )

    # --- Identify Rows for Logging ---
    # Rows are logged if:
    # 1. Their rank is not 'species' or 'subspecies' (higher ranks).
    # 2. Their rank is 'species' or 'subspecies' BUT they didn't find a match in Excel.
    ranks_to_match = ["species", "subspecies"]
    is_higher_rank = ~df_processing[CSV_RANK_COL].isin(ranks_to_match)
    is_unmatched_species_subspecies = df_processing[CSV_RANK_COL].isin(ranks_to_match) & (df_processing["_merge"] == "left_only")
    log_mask = is_higher_rank | is_unmatched_species_subspecies

    # --- Process DataFrame for Main Output (applies to all rows) ---
    # Fill NaNs in the original criteria columns (from Excel) with "No".
    # This handles higher ranks and unmatched species/subspecies.
    df_processing[criteria_cols] = df_processing[criteria_cols].fillna("No")

    rename_mapping = {
        col: col.replace("Kriterium_", "", 1).replace("_", " ")
        for col in criteria_cols
        # Ensure we only try to rename columns that actually exist after the merge
        if col in df_processing.columns
    }
    df_processing.rename(columns=rename_mapping, inplace=True)

    # Prepare the final main output DataFrame by dropping the merge indicator
    df_main_output_to_save = df_processing.drop(columns=["_merge"])

    # Save the main processed file (contains all original rows)
    df_main_output_to_save.to_csv(output_path, index=False, sep=";")
    print(f"Processed data (all rows) saved to: {output_path}")

    # --- Prepare and save log file for unmatched/higher_rank rows ---
    # Select the rows to be logged from the fully processed DataFrame (df_main_output_to_save)
    # using the log_mask.
    df_log_data = df_main_output_to_save[log_mask].copy()

    if not df_log_data.empty:
        log_file_name = Path(output_path).stem + "_unmatched_log.csv"
        log_output_path = Path(output_path).parent / log_file_name
        df_log_data.to_csv(log_output_path, index=False, sep=";")
        print(f"Log of {len(df_log_data)} unmatched/higher-rank rows saved to: {log_output_path}")
    else:
        print("No rows needed to be logged for unmatched/higher-rank status.")

    return output_path


##### Execution Entry Point #####


## Function: main ##
def main(cleaned_csv_path, excel_path, output_path):
    # Minimal wrapper, no type hints.
    return add_forvaltning_columns(cleaned_csv_path, excel_path, output_path)


if __name__ == "__main__":
    pass  # Minimal block as requested.

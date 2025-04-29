import pandas as pd
from pathlib import Path  # Re-enabled as it will be used by the main script


##### Configuration #####
# Column name for scientific names in the Excel file. Modify if source changes.
EXCEL_SPECIES_COL = 'Vitenskapelig_Navn'
# Column name for scientific names in the CSV file. Modify if source changes.
CSV_SPECIES_COL = 'validScientificName'
# 0-based index (5th col) in Excel where criteria cols start.
# Adjust if Excel layout changes.
CRITERIA_START_COL_INDEX = 4


# The get_criteria_string function is removed as it's no longer needed.


##### Main Logic #####

## Function: add_forvaltning_columns ##
def add_forvaltning_columns(
    cleaned_csv_path,  # Input CSV path.
    excel_path,        # Input Excel path.
    output_path        # Output CSV path.
):
    # --- Load data (Happy Path Only) ---
    # Reads the first sheet by default. Assumes file exists and is valid.
    df_excel = pd.read_excel(excel_path)
    # Assumes ';' separator. Assumes file exists and is valid.
    df_csv_cleaned = pd.read_csv(cleaned_csv_path, sep=';')

    # --- Identify and Prepare Criteria Columns from Excel ---
    # Get columns starting from the defined index.
    potential_criteria_cols = df_excel.columns[CRITERIA_START_COL_INDEX:]
    # Filter for columns that actually start with 'Kriterium'.
    criteria_cols = [
        col for col in potential_criteria_cols if col.startswith('Kriterium')
    ]

    # Set the species name as the index for easy mapping.
    # Assumes EXCEL_SPECIES_COL exists and is suitable index.
    df_excel_indexed = df_excel.set_index(EXCEL_SPECIES_COL)

    # Create a DataFrame containing only the criteria columns with Yes/No.
    df_criteria_bool = pd.DataFrame(index=df_excel_indexed.index)
    for col in criteria_cols:
        # Check if column exists before processing
        if col in df_excel_indexed.columns:
            # Convert 'X' (case-insensitive, stripped) to 'Yes', others 'No'.
            is_x = df_excel_indexed[col].astype(str).str.strip().str.upper()
            df_criteria_bool[col] = is_x.eq('X').map({True: 'Yes', False: 'No'})
        # else: # Handle missing columns if needed, currently skipped
            # print(f"Warning: Expected criteria column '{col}' not found.")

    # --- Merge Criteria into Cleaned CSV Data ---
    # Merge based on species name. Keep all rows from the cleaned CSV.
    # Assumes CSV_SPECIES_COL exists in df_csv_cleaned.
    df_merged = pd.merge(
        df_csv_cleaned,
        df_criteria_bool,
        left_on=CSV_SPECIES_COL,  # Key from the left DataFrame (CSV)
        right_index=True,         # Key from the right (Excel criteria map)
        how='left'                # Keep all rows from left (CSV)
    )

    # Fill criteria columns with 'No' for species present in CSV
    # but not in Excel map.
    df_merged[criteria_cols] = df_merged[criteria_cols].fillna('No')

    # --- Rename Criteria Columns ---
    # Create a dictionary mapping old names to new names (strip prefix)
    rename_mapping = {
        # Strip 'Kriterium_' prefix (1st occurrence)
        col: col.replace('Kriterium_', '', 1) for col in criteria_cols
        # Ensure column exists in merged df before adding to mapping
        if col in df_merged.columns
    }
    # Apply the renaming to the DataFrame.
    df_merged = df_merged.rename(columns=rename_mapping)

    # The old logic for 'forvaltningsinteresse_kriterium' and
    # 'is_forvaltningsinteresse' is replaced by the merge.

    # --- Save result ---
    # Saves. Assumes output path is valid and writable.
    df_merged.to_csv(output_path, index=False, sep=';')
    # Return the output path (part of core function)
    return output_path


##### Execution Entry Point #####

## Function: main ##
def main(cleaned_csv_path, excel_path, output_path):
    # Minimal wrapper, no type hints.
    return add_forvaltning_columns(cleaned_csv_path, excel_path, output_path)


if __name__ == "__main__":
    pass  # Minimal block as requested.
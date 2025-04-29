import pandas as pd
from pathlib import Path

# Configuration
EXCEL_SPECIES_COL = 'Vitenskapelig_Navn'
CSV_SPECIES_COL = 'validScientificName'
CRITERIA_START_COL_INDEX = 4 # 5th column in the excel file

def get_criteria_string(row, criteria_cols):
    """Returns comma-separated string of criteria with 'X' and starting with 'Kriterium'."""
    marked_criteria = [
        col for col in criteria_cols
        # Only include if marked with 'X' AND name starts with 'Kriterium'
        if str(row.get(col, '')).strip().upper() == 'X' and col.startswith('Kriterium')
    ]
    return ', '.join(marked_criteria) if marked_criteria else None

def add_forvaltning_columns(
    cleaned_csv_path: Path, 
    excel_path: Path, 
    output_path: Path
) -> Path | None:
    """Main function to add conservation interest columns to the data."""
    # Load data
    try:
        print(f"Loading Excel data from {excel_path}...")
        df_excel = pd.read_excel(excel_path)
        print(f"Loading cleaned CSV from {cleaned_csv_path}...")
        df_csv_cleaned = pd.read_csv(cleaned_csv_path, sep=';')
    except FileNotFoundError as e:
        print(f"Error loading input file: {e}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
    # Create mapping from Excel data
    potential_criteria_cols = df_excel.columns[CRITERIA_START_COL_INDEX:]
    df_excel['criteria_string'] = df_excel.apply(
        lambda row: get_criteria_string(row, potential_criteria_cols), axis=1
    )
    criteria_map = (
        df_excel.dropna(subset=['criteria_string'])
        .set_index(EXCEL_SPECIES_COL)['criteria_string']
    )
    
    # Add conservation interest columns to cleaned data
    df_csv_cleaned['forvaltningsinteresse_kriterium'] = df_csv_cleaned[
        CSV_SPECIES_COL
    ].map(criteria_map)
    df_csv_cleaned['is_forvaltningsinteresse'] = df_csv_cleaned[
        'forvaltningsinteresse_kriterium'
    ].notna()
    
    # Save result
    df_csv_cleaned.to_csv(output_path, index=False, sep=';')
    return output_path

def main(cleaned_csv_path: Path, excel_path: Path, output_path: Path) -> Path | None:
    return add_forvaltning_columns(cleaned_csv_path, excel_path, output_path)
if __name__ == "__main__":
    # Example of how to run directly (requires manual path setting)
    print("Running augmenter script directly requires manual path configuration.")

    pass # Prevent direct execution without paths
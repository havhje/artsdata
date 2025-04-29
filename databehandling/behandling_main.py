##### Imports #####
import sys
from pathlib import Path

# Dynamically add the script directory to sys.path to allow importing siblings
# This assumes the script is run from the workspace root or the
# databehandling directory.
script_dir = Path(__file__).parent.resolve()
module_dir = script_dir / 'data_manipulasjon'
sys.path.insert(0, str(module_dir.parent))  # Add databehandling parent dir

# Import the main functions from the sibling modules
from data_manipulasjon import cleans_columns
from data_manipulasjon import adds_forvaltningsinteresse


##### Configuration #####

# Define base directory relative to this script's location
BASE_DIR = Path(__file__).parent.resolve()

# Input data paths. Modify filenames if they change.
INPUT_DIR = BASE_DIR / 'input_artsdata'
RAW_CSV_FILENAME = 'fuglsortland.csv'
RAW_CSV_PATH = INPUT_DIR / RAW_CSV_FILENAME  # Path to the initial raw data file.

# Metadata path. Modify filename if it changes.
METADATA_DIR = BASE_DIR / 'metadata_add'
EXCEL_FILENAME = 'ArtslisteArtnasjonal_2023_01-31.xlsx'
EXCEL_PATH = METADATA_DIR / EXCEL_FILENAME  # Path to the Excel metadata file.

# Output directory and filenames. Modify as needed.
OUTPUT_DIR = BASE_DIR / 'output'
CLEANED_CSV_FILENAME = f"{RAW_CSV_FILENAME.stem}_cleaned.csv" # e.g., fuglsortland_cleaned.csv
CLEANED_CSV_PATH = OUTPUT_DIR / CLEANED_CSV_FILENAME # Intermediate cleaned file path.
FINAL_CSV_FILENAME = f"{RAW_CSV_FILENAME.stem}_processed.csv" # e.g., fuglsortland_processed.csv
FINAL_CSV_PATH = OUTPUT_DIR / FINAL_CSV_FILENAME   # Final output file path.


##### Main Processing Logic #####

## Function: run_processing ##
def run_processing():
    # Orchestrates the entire data cleaning and enrichment pipeline.
    # Assumes all input files exist and output directory is creatable/writable.

    # --- Ensure output directory exists (Minimal side-effect) ---
    # This is a minimal deviation for usability, as the script must write output.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True) # Creates dir if not present.

    # --- Step 1: Clean Columns ---
    # Calls the main function from cleans_columns script.
    # Takes raw CSV path, outputs to intermediate cleaned path.
    # Assumes cleans_columns.main returns the output path on success.
    intermediate_path = cleans_columns.main(RAW_CSV_PATH, CLEANED_CSV_PATH)

    # --- Step 2: Add Forvaltningsinteresse Columns ---
    # Calls the main function from adds_forvaltningsinteresse script.
    # Takes intermediate cleaned path and Excel path, outputs to final path.
    # Assumes adds_forvaltningsinteresse.main returns the output path on success.
    final_path = adds_forvaltningsinteresse.main(
        intermediate_path,  # Use the path returned by the previous step
        EXCEL_PATH,
        FINAL_CSV_PATH
    )

    # Return the final output path for potential use by a caller.
    return final_path


##### Execution Entry Point #####

if __name__ == "__main__":
    # This block executes only when the script is run directly.
    # It calls the main orchestration function.
    run_processing() # Executes the defined data processing pipeline.

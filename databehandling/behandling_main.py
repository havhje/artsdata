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
from data_manipulasjon import api_artsdata


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
# Use the Path object RAW_CSV_PATH to get the stem
CLEANED_CSV_FILENAME = f"{RAW_CSV_PATH.stem}_cleaned.csv" # e.g., fuglsortland_cleaned.csv
CLEANED_CSV_PATH = OUTPUT_DIR / CLEANED_CSV_FILENAME # Intermediate cleaned file path.
# Use the Path object RAW_CSV_PATH to get the stem
PROCESSED_CSV_FILENAME = f"{RAW_CSV_PATH.stem}_processed.csv" # e.g., fuglsortland_processed.csv
PROCESSED_CSV_PATH = OUTPUT_DIR / PROCESSED_CSV_FILENAME   # Intermediate after criteria add
# Use the Path object RAW_CSV_PATH to get the stem
FINAL_CSV_FILENAME = f"{RAW_CSV_PATH.stem}_taxonomy.csv" # e.g., fuglsortland_taxonomy.csv
FINAL_CSV_PATH = OUTPUT_DIR / FINAL_CSV_FILENAME # Final output file path after taxonomy.


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
    cleaned_path = cleans_columns.main(RAW_CSV_PATH, CLEANED_CSV_PATH)
    # Minimal check: ensure previous step returned a path (didn't fail)
    if not cleaned_path:
        # print("Error: Column cleaning step failed.")
        return None # Stop processing

    # --- Step 2: Add Forvaltningsinteresse Columns ---
    # Calls the main function from adds_forvaltningsinteresse script.
    # Takes cleaned path and Excel path, outputs to processed path.
    # Assumes adds_forvaltningsinteresse.main returns the output path on success.
    processed_path = adds_forvaltningsinteresse.main(
        cleaned_path,  # Use the path returned by the previous step
        EXCEL_PATH,
        PROCESSED_CSV_PATH # Save to intermediate processed path
    )
    # Minimal check
    if not processed_path:
        # print("Error: Adding forvaltningsinteresse step failed.")
        return None # Stop processing

    # --- Step 3: Add Taxonomy Columns via API ---
    # Calls the main function from api_artsdata script.
    # Takes processed path, outputs to final taxonomy path.
    # Assumes api_artsdata.main returns the output path on success.
    final_path = api_artsdata.main(
        processed_path, # Use the path returned by the previous step
        FINAL_CSV_PATH
    )
    # Minimal check
    if not final_path:
        # print("Error: Adding taxonomy step failed.")
        return None # Stop processing

    # Return the final output path for potential use by a caller.
    return final_path


##### Execution Entry Point #####

if __name__ == "__main__":
    # This block executes only when the script is run directly.
    # It calls the main orchestration function.
    # print("Starting data processing pipeline...") # Keep prints minimal
    final_output_file = run_processing()
    # Check if the pipeline completed (returned a file path)
    if final_output_file:
        # Print success message only if pipeline ran without returning None.
        print(f"Pipeline completed successfully. Final output: {final_output_file}")
    # else:
        # print("Pipeline failed.") # Keep prints minimal
        # Pass if failed, as individual steps might have indicated errors (future).
        pass

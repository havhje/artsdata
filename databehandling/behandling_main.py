##### Imports #####
import sys
import argparse # Import argparse for command-line arguments
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


##### Default Configuration (used if not overridden by args) #####

# Define base directory relative to this script's location
# Used primarily for default argument calculation
_BASE_DIR = Path(__file__).parent.resolve()
_DEFAULT_INPUT_DIR = _BASE_DIR / 'input_artsdata'
_DEFAULT_METADATA_DIR = _BASE_DIR / 'metadata_add'
_DEFAULT_OUTPUT_DIR = _BASE_DIR / 'output'
_DEFAULT_EXCEL_FILENAME = 'ArtslisteArtnasjonal_2023_01-31.xlsx'


##### Main Processing Logic #####

## Function: run_processing ##
def run_processing(input_csv_path, excel_meta_path, output_dir):
    # Orchestrates the entire data cleaning and enrichment pipeline.
    # Takes input paths and output directory as arguments.
    # Assumes input files exist and output directory is creatable/writable.

    # --- Define intermediate/output filenames based on input --- 
    cleaned_csv_filename = f"{input_csv_path.stem}_cleaned.csv"
    cleaned_csv_path = output_dir / cleaned_csv_filename
    processed_csv_filename = f"{input_csv_path.stem}_processed.csv"
    processed_csv_path = output_dir / processed_csv_filename
    final_csv_filename = f"{input_csv_path.stem}_taxonomy.csv"
    final_csv_path = output_dir / final_csv_filename

    # --- Ensure output directory exists (Minimal side-effect) ---
    # This is a minimal deviation for usability, as the script must write output.
    output_dir.mkdir(parents=True, exist_ok=True) # Creates dir if not present.

    # --- Step 1: Clean Columns ---
    # Calls the main function from cleans_columns script.
    # Takes raw CSV path, outputs to intermediate cleaned path.
    # Assumes cleans_columns.main returns the output path on success.
    cleaned_path = cleans_columns.main(input_csv_path, cleaned_csv_path)
    # Minimal check: ensure previous step returned a path (didn't fail)
    if not cleaned_path:
        # print("Error: Column cleaning step failed.")
        return None # Stop processing

    # --- Step 2: Add Forvaltningsinteresse Columns ---
    # Calls the main function from adds_forvaltningsinteresse script.
    # Takes cleaned path and Excel path, outputs to processed path.
    # Assumes adds_forvaltningsinteresse.main returns the output path on success.
    processed_path = adds_forvaltningsinteresse.main(
        cleaned_path,       # Use the path returned by the previous step
        excel_meta_path,    # Use the provided metadata path
        processed_csv_path  # Save to intermediate processed path
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
        final_csv_path
    )
    # Minimal check
    if not final_path:
        # print("Error: Adding taxonomy step failed.")
        return None # Stop processing

    # Return the final output path for potential use by a caller.
    return final_path


##### Execution Entry Point #####

if __name__ == "__main__":
    # --- Argument Parsing --- 
    parser = argparse.ArgumentParser(
        description="Clean and enrich species observation data from Artsdatabanken."
    )
    # Required input file argument
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the raw input CSV file."
    )
    # Optional metadata file argument
    parser.add_argument(
        "--metadata",
        type=str,
        default=str(_DEFAULT_METADATA_DIR / _DEFAULT_EXCEL_FILENAME),
        help=f"Path to the Excel metadata file (default: derived from script location)"
    )
    # Optional output directory argument
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(_DEFAULT_OUTPUT_DIR),
        help="Directory to save the output files (default: 'output' next to script)"
    )

    args = parser.parse_args() # Parse the command-line arguments

    # Convert paths from strings to Path objects
    input_path = Path(args.input_file)
    metadata_path = Path(args.metadata)
    output_path_dir = Path(args.output_dir)

    # --- Run Pipeline --- 
    # This block executes only when the script is run directly.
    # It calls the main orchestration function with parsed arguments.
    # print("Starting data processing pipeline...") # Keep prints minimal
    final_output_file = run_processing(input_path, metadata_path, output_path_dir)
    
    # Check if the pipeline completed (returned a file path)
    if final_output_file:
        # Print success message only if pipeline ran without returning None.
        print(f"Pipeline completed successfully. Final output: {final_output_file}")
    # else:
        # print("Pipeline failed.") # Keep prints minimal
        # Pass if failed, as individual steps might have indicated errors (future).
        pass

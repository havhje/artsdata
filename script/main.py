import sys
from pathlib import Path
import argparse # Import argparse for command-line arguments
import os # Import os for file deletion

# --- Setup Project Path ---
# Get the directory of the current script (main.py)
script_dir = Path(__file__).resolve().parent
# Assume the project root is one level up
project_root = script_dir.parent
# Add the project root to the Python path
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# --- Import Data Processing Functions ---
try:
    from script.Datatreatment.csv_column_cleaner import main as run_cleaner
    from script.Datatreatment.csv_add_columns_arter import main as run_augmenter
    print("Successfully imported data processing functions.")
except ImportError as e:
    print(f"Error: Failed to import data processing scripts: {e}")
    print("Ensure main.py is in the 'script' directory and the structure is correct.")
    sys.exit(1)

# --- Argument Parsing ---
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the data cleaning and augmentation pipeline.")
    parser.add_argument("input_csv", help="Name of the input CSV file (e.g., fuglsortland.csv) located in the 'artsdata' directory.")
    parser.add_argument("--keep-intermediate", action="store_true", help="Keep the intermediate cleaned CSV file.")
    return parser.parse_args()

# --- Main Orchestration Logic ---
def main():
    args = parse_arguments()
    input_filename = args.input_csv
    keep_intermediate = args.keep_intermediate

    print(f"\nStarting data processing pipeline for {input_filename}...")

    # Define paths based on input filename
    arts_data_dir = project_root / "artsdata"
    output_dir = project_root / "output"  # Define base output directory
    intermediate_dir = output_dir / "intermediate"
    final_dir = output_dir / "final"
    
    # Create output directories if they don't exist
    intermediate_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)

    raw_csv_path = arts_data_dir / input_filename

    # Generate output filenames
    base_name = Path(input_filename).stem # Get filename without extension
    # Update paths to use new output directories
    cleaned_csv_path = intermediate_dir / f"{base_name}_cleaned.csv"
    augmented_csv_path = final_dir / f"{base_name}_forvaltning.csv"
    excel_path = arts_data_dir / "ArtslisteArtnasjonal_2023_01-31.xlsx" # Excel path remains static for now

    # Check if input file exists
    if not raw_csv_path.is_file():
        print(f"\nError: Input file not found at {raw_csv_path}")
        sys.exit(1)

    # Step 1: Run Data Cleaning
    print("\n=== Step 1: Running Data Cleaning ===")
    # Pass paths to the cleaner function
    cleaned_file_result = run_cleaner(raw_csv_path, cleaned_csv_path)

    if not cleaned_file_result:
        print("\nError: Data cleaning failed. Aborting pipeline.")
        sys.exit(1)

    print(f"\nData cleaning successful. Intermediate file: {cleaned_csv_path}") # Updated log message

    # Step 2: Run Data Augmentation
    print("\n=== Step 2: Running Data Augmentation ===")
    # Pass paths to the augmenter function
    augmented_file_result = run_augmenter(cleaned_csv_path, excel_path, augmented_csv_path)

    if not augmented_file_result:
        print("\nError: Data augmentation failed.")
        # Optionally delete intermediate file even on failure if it exists?
        # The cleanup logic below will handle this based on the keep_intermediate flag
        sys.exit(1)

    print(f"\nData augmentation successful. Final file: {augmented_csv_path}")

    # --- Cleanup Intermediate File ---
    if not keep_intermediate:
        if cleaned_csv_path.is_file():
            try:
                os.remove(cleaned_csv_path) # Path is already updated
                print(f"Removed intermediate file: {cleaned_csv_path}")
            except OSError as e:
                print(f"Error removing intermediate file {cleaned_csv_path}: {e}")
        else:
            print(f"Intermediate file {cleaned_csv_path} not found for removal.")
    else:
        print(f"Keeping intermediate file: {cleaned_csv_path}")

    print("\nData processing pipeline finished successfully!")

# --- Script Entry Point ---
if __name__ == "__main__":
    main()
# Data Processing Pipeline Documentation

## Purpose

This directory contains a Python pipeline designed to clean and enrich species observation data, typically exported from systems like Artsdatabanken. The pipeline performs several steps:

1.  **Cleans Data**: Removes predefined unnecessary columns from the raw input CSV.
2.  **Adds Conservation Criteria**: Merges data from an Excel file to add columns indicating conservation criteria (e.g., Red List status based on 'Kriterium_' columns) for each species.
3.  **Adds Taxonomy**: Fetches taxonomic hierarchy (Kingdom, Phylum, Class, Order, Family, Genus) and Norwegian vernacular names for Order and Family ranks from the NorTaxa API based on the species' `validScientificNameId`.

## Project Structure

```
databehandling/
├── behandling_main.py          # Main orchestration script
├── data_manipulasjon/        # Directory for individual processing modules
│   ├── __init__.py
│   ├── cleans_columns.py         # Module for cleaning columns
│   ├── adds_forvaltningsinteresse.py # Module for adding conservation criteria
│   └── api_artsdata.py           # Module for fetching taxonomy via API
├── input_artsdata/           # Directory for raw input CSV files
│   └── fuglsortland.csv          # Example input file
├── metadata_add/             # Directory for metadata files
│   └── ArtslisteArt...xlsx     # Excel file with conservation criteria
├── output/                   # Directory for processed output files (created automatically)
│   ├── fuglsortland_cleaned.csv    # Intermediate output after cleaning
│   ├── fuglsortland_processed.csv  # Intermediate output after adding criteria
│   ├── fuglsortland_processed_unmatched_log.csv # Log of unmatched/higher-rank taxa
│   └── fuglsortland_taxonomy.csv   # Final output with taxonomy
├── test_databehandling/        # Directory for test scripts
│   └── api_test                  # Simple script to test API calls
└── databehandling_project_info.md # This documentation file
```

## Workflow

The main script `behandling_main.py` controls the workflow:

1. **Configuration**: Defines input filenames, metadata filenames, and output filenames and paths based on the directory structure.
2. **Output Directory Creation**: Ensures the `output/` directory exists.
3. **Step 1: Clean Columns**: Calls `cleans_columns.main()`, passing the raw input CSV path and the path for the cleaned output.
    * `cleans_columns.py` loads the raw CSV, drops a predefined list of columns, processes the `individualCount` column (fills NaN with 1, converts to Int64), and saves the result.
4. **Step 2: Add Conservation Criteria**: Calls `adds_forvaltningsinteresse.main()`, passing the cleaned CSV path from Step 1, the Excel metadata path, and the path for the processed output.
    * `adds_forvaltningsinteresse.py` loads the cleaned CSV and the Excel file (specifically, the sheet defined by `EXCEL_SHEET_NAME`).
    * It identifies criteria columns in the Excel sheet (those starting with `CRITERIA_COL_PREFIX`, e.g., `Kriterium_`).
    * It converts the 'X' markers in these criteria columns to 'Yes' and fills any missing values (NaN) with 'No', ensuring all criteria cells have a clear 'Yes' or 'No'.
    * The script performs a **left merge** from the input CSV to the Excel criteria data, using `validScientificNameId` (defined by `CSV_ID_COL` and `EXCEL_ID_COL`) as the merge key. This ensures **all rows from the input CSV are retained** in the main processed output.
    * For rows in the input CSV that represent a **higher taxonomic rank** (i.e., `scientificNameRank` is not 'species' or 'subspecies') or for **species/subspecies whose `validScientificNameId` is not found** in the Excel criteria sheet, their conservation criteria columns in the main output are populated with "No".
    * These specific rows (higher rank or unmatched species/subspecies) are also **logged to a separate CSV file**. This log file includes a `log_reason` column indicating why the row was logged ("Higher taxonomic rank" or "Species/subspecies ID not found in Excel").
    * The criteria columns in the main output are renamed (removing the prefix and replacing `_` with a space).
    * The main processed DataFrame (with all original rows and added/updated criteria) is saved. The log DataFrame is saved to its own file.
5. **Step 3: Add Taxonomy**: Calls `api_artsdata.main()`, passing the processed CSV path from Step 2 and the path for the final output.
    * `api_artsdata.py` loads the processed CSV. It identifies unique `validScientificNameId` values.
    * For each unique ID, it calls the NorTaxa API (`/api/v1/TaxonName/ByScientificNameId/{id}`) to get species data.
    * It extracts the taxonomic hierarchy (Kingdom to Genus) and the `scientificNameId` for the Family and Order ranks.
    * It calls the API again using the Family ID and Order ID to fetch their respective data.
    * It extracts the Norwegian vernacular names for Family and Order (prioritizing Bokmål 'nb').
    * It adds new columns for each taxonomic rank (`Kingdom`, `Phylum`, ..., `Genus`) and the Norwegian names (`FamilieNavn`, `OrdenNavn`) to the DataFrame.
    * It saves the final enriched DataFrame.
6. **Completion**: If all steps complete successfully, `behandling_main.py` prints a success message indicating the final output file path.


# Basic usage (using default metadata and output directory with uv)
uv run -- python databehandling/behandling_main.py databehandling/input_artsdata/Andøya_fugl.csv

# Specifying metadata file with uv
uv run -- python databehandling/behandling_main.py path/to/your/input_file.csv --metadata path/to/your/metadata.xlsx

# Specifying output directory with uv
uv run -- python databehandling/behandling_main.py path/to/your/input_file.csv --output-dir path/to/your/output

# Specifying both with uv
uv run -- python databehandling/behandling_main.py path/to/your/input_file.csv --metadata path/to/your/metadata.xlsx --output-dir path/to/your/output

# Example with a specific input file path (Andøya_fugl.csv) from the workspace root (using uv)
uv run -- python databehandling/behandling_main.py databehandling/input_artsdata/Andøya_fugl.csv
```

**Command-line arguments:**

*   `input_file.csv`: **(Required)** The path to the raw CSV data you want to process.
*   `--metadata` (Optional): Path to the Excel file containing conservation criteria. Defaults to `databehandling/metadata_add/ArtslisteArtnasjonal_2023_01-31.xlsx` relative to the `databehandling` directory.
*   `--output-dir` (Optional): Directory where the intermediate and final processed files will be saved. Defaults to `databehandling/output/` relative to the `databehandling` directory.

**Prerequisites before running:**

1.  ~~Ensure the required input file (`fuglsortland.csv` or similar) is placed in the `databehandling/input_artsdata/` directory.~~ (This is no longer necessary as the input file is specified as an argument).
2.  Ensure the required Excel metadata file (e.g., `ArtslisteArtnasjonal_2023_01-31.xlsx`) exists at the location specified by the `--metadata` argument (or its default location in `databehandling/metadata_add/`).
3.  Make sure the dependencies are installed (see Setup).
4.  Ensure you have navigated to the workspace root directory (`artsdata`) in your terminal before running the commands above.

Upon successful completion, the final output file (e.g., `input_file_taxonomy.csv`) will be located in the specified output directory, along with the intermediate files (`input_file_cleaned.csv`, `input_file_processed.csv`, and `input_file_processed_unmatched_log.csv`).

## Configuration Notes

*   **File Paths/Names**: The *input* file path is now provided via command-line argument. Default paths for metadata and output directory are set in `behandling_main.py` but can be overridden via arguments. Output filenames are generated based on the input filename stem.
*   **Column Names**: Key column names used for merging or processing (e.g., `validScientificNameId`, `Vitenskapelig_Navn`, `individualCount`) are defined as constants or used directly in the respective `.py` files within `data_manipulasjon/`. Adjust these if the source data schema changes.
*   **Columns to Drop**: The list of columns removed in the cleaning step is hardcoded in `cleans_columns.py`.
*   **Criteria Columns**: The logic for identifying and renaming criteria columns (prefix `CRITERIA_COL_PREFIX`, start index for renaming) is in `adds_forvaltningsinteresse.py`. The script now uses `validScientificNameId` for matching. It also generates a log file for entries that are of higher taxonomic rank or are species/subspecies not found in the criteria Excel file.
*   **API Endpoint**: The NorTaxa API base URL is configured in `api_artsdata.py`.
*   **Taxonomic Ranks**: The specific ranks extracted from the API are defined in `api_artsdata.py` (`desired_ranks`).

## Current State & Future Improvements

*   **Minimal Implementation**: These scripts currently follow "minimal functional logic" principles. They lack comprehensive error handling (e.g., for missing files, invalid data, API errors, network issues), logging, type hinting, and docstrings.
*   **Error Handling**: Adding robust error handling (e.g., `try...except` blocks, checking API response codes, validating data) is highly recommended before using this in production or with varied datasets.
*   **Logging**: Implementing logging would provide better insight into the pipeline's execution and potential issues.
*   **Testing**: Formal unit/integration tests (e.g., using `pytest`) should be added to verify the logic of each component, especially the data transformations and API interactions.
*   **Configuration Management**: For more complex scenarios, consider moving configuration values (paths, column names, API keys if needed) out into a separate configuration file (e.g., YAML, TOML, .env).
*   **Parallelization**: For very large datasets, the API fetching step could potentially be parallelized to improve performance (though care must be taken not to overload the API).

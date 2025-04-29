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
│   └── fuglsortland_taxonomy.csv   # Final output with taxonomy
├── test_databehandling/        # Directory for test scripts
│   └── api_test                  # Simple script to test API calls
└── databehandling_project_info.md # This documentation file
```

## Workflow

The main script `behandling_main.py` controls the workflow:

1.  **Configuration**: Defines input filenames, metadata filenames, and output filenames and paths based on the directory structure.
2.  **Output Directory Creation**: Ensures the `output/` directory exists.
3.  **Step 1: Clean Columns**: Calls `cleans_columns.main()`, passing the raw input CSV path and the path for the cleaned output.
    *   `cleans_columns.py` loads the raw CSV, drops a predefined list of columns, processes the `individualCount` column (fills NaN with 1, converts to Int64), and saves the result.
4.  **Step 2: Add Conservation Criteria**: Calls `adds_forvaltningsinteresse.main()`, passing the cleaned CSV path from Step 1, the Excel metadata path, and the path for the processed output.
    *   `adds_forvaltningsinteresse.py` loads the cleaned CSV and the Excel file. It identifies criteria columns in Excel (starting with `Kriterium_`), converts the 'X' markers to 'Yes'/'No', merges these columns into the CSV based on scientific name, renames the criteria columns (removing prefix and replacing `_` with space), and saves the result.
5.  **Step 3: Add Taxonomy**: Calls `api_artsdata.main()`, passing the processed CSV path from Step 2 and the path for the final output.
    *   `api_artsdata.py` loads the processed CSV. It identifies unique `validScientificNameId` values.
    *   For each unique ID, it calls the NorTaxa API (`/api/v1/TaxonName/ByScientificNameId/{id}`) to get species data.
    *   It extracts the taxonomic hierarchy (Kingdom to Genus) and the `scientificNameId` for the Family and Order ranks.
    *   It calls the API again using the Family ID and Order ID to fetch their respective data.
    *   It extracts the Norwegian vernacular names for Family and Order (prioritizing Bokmål 'nb').
    *   It adds new columns for each taxonomic rank (`Kingdom`, `Phylum`, ..., `Genus`) and the Norwegian names (`FamilieNavn`, `OrdenNavn`) to the DataFrame.
    *   It saves the final enriched DataFrame.
6.  **Completion**: If all steps complete successfully, `behandling_main.py` prints a success message indicating the final output file path.

## Setup

### Dependencies

This pipeline relies on the following Python libraries:

*   `pandas`: For data manipulation and CSV/Excel handling.
*   `requests`: For making HTTP calls to the NorTaxa API.
*   `tqdm`: For displaying a progress bar during API calls.

### Installation (using uv)

It is recommended to use `uv` for package management. Ensure `uv` is installed. Then, from the workspace root (`artsdata` directory), run:

```bash
uv add pandas requests tqdm
```

Alternatively, if using `pip` and `venv`:

```bash
python -m venv .venv
source .venv/bin/activate # Or .\venv\Scripts\activate on Windows
pip install pandas requests tqdm
```

## Usage

To run the entire processing pipeline:

1.  ~~Ensure the required input file (`fuglsortland.csv` or similar) is placed in the `databehandling/input_artsdata/` directory.~~ (This is no longer necessary as the input file is specified as an argument).
2.  Ensure the required Excel metadata file (e.g., `ArtslisteArtnasjonal_2023_01-31.xlsx`) exists at the location specified by the `--metadata` argument (or its default location in `databehandling/metadata_add/`).
3.  Make sure the dependencies are installed (see Setup).
4.  Navigate to the workspace root directory (`artsdata`) in your terminal.
5.  Run the main script, providing the path to the input CSV file as the first argument. You can optionally specify the metadata file and output directory:

    ```bash
    # Basic usage (using default metadata and output directory)
    python databehandling/behandling_main.py path/to/your/input_file.csv

    # Specifying metadata file
    python databehandling/behandling_main.py path/to/your/input_file.csv --metadata path/to/your/metadata.xlsx

    # Specifying output directory
    python databehandling/behandling_main.py path/to/your/input_file.csv --output-dir path/to/your/output

    # Specifying both
    python databehandling/behandling_main.py path/to/your/input_file.csv --metadata path/to/your/metadata.xlsx --output-dir path/to/your/output
    ```

    *   `input_file.csv`: **(Required)** The path to the raw CSV data you want to process.
    *   `--metadata` (Optional): Path to the Excel file containing conservation criteria. Defaults to `databehandling/metadata_add/ArtslisteArtnasjonal_2023_01-31.xlsx` relative to the `databehandling` directory.
    *   `--output-dir` (Optional): Directory where the intermediate and final processed files will be saved. Defaults to `databehandling/output/` relative to the `databehandling` directory.

Upon successful completion, the final output file (e.g., `input_file_taxonomy.csv`) will be located in the specified output directory, along with the intermediate files (`input_file_cleaned.csv`, `input_file_processed.csv`).

## Configuration Notes

*   **File Paths/Names**: The *input* file path is now provided via command-line argument. Default paths for metadata and output directory are set in `behandling_main.py` but can be overridden via arguments. Output filenames are generated based on the input filename stem.
*   **Column Names**: Key column names used for merging or processing (e.g., `validScientificNameId`, `Vitenskapelig_Navn`, `individualCount`) are defined as constants or used directly in the respective `.py` files within `data_manipulasjon/`. Adjust these if the source data schema changes.
*   **Columns to Drop**: The list of columns removed in the cleaning step is hardcoded in `cleans_columns.py`.
*   **Criteria Columns**: The logic for identifying and renaming criteria columns (prefix `Kriterium_`, start index) is in `adds_forvaltningsinteresse.py`.
*   **API Endpoint**: The NorTaxa API base URL is configured in `api_artsdata.py`.
*   **Taxonomic Ranks**: The specific ranks extracted from the API are defined in `api_artsdata.py` (`desired_ranks`).

## Current State & Future Improvements

*   **Minimal Implementation**: These scripts currently follow "minimal functional logic" principles. They lack comprehensive error handling (e.g., for missing files, invalid data, API errors, network issues), logging, type hinting, and docstrings.
*   **Error Handling**: Adding robust error handling (e.g., `try...except` blocks, checking API response codes, validating data) is highly recommended before using this in production or with varied datasets.
*   **Logging**: Implementing logging would provide better insight into the pipeline's execution and potential issues.
*   **Testing**: Formal unit/integration tests (e.g., using `pytest`) should be added to verify the logic of each component, especially the data transformations and API interactions.
*   **Configuration Management**: For more complex scenarios, consider moving configuration values (paths, column names, API keys if needed) out into a separate configuration file (e.g., YAML, TOML, .env).
*   **Parallelization**: For very large datasets, the API fetching step could potentially be parallelized to improve performance (though care must be taken not to overload the API).

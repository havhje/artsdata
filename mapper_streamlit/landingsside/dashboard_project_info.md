# Streamlit Dashboard Documentation (`landingsside`)

## Purpose

This directory contains the Streamlit components responsible for generating and displaying the main summary dashboard for the species observation data. It takes processed data (expected output from the `databehandling` pipeline) and presents key metrics, counts, and top lists in an interactive web interface.

## Project Structure

```
mapper_streamlit/
└── landingsside/
    ├── dashboard.py                     # Main dashboard orchestration script
    ├── utils_dashboard/                 # Directory for dashboard utility modules
    │   ├── __init__.py                  # (Likely present or should be added)
    │   ├── formatting.py                # Module for formatting data into markdown
    │   ├── calculations/                # Subdirectory for data calculation modules
    │   │   ├── __init__.py              # (Likely present or should be added)
    │   │   ├── calculate_basic_metrics.py # Calculates overall totals, uniques, dates
    │   │   ├── calculate_redlists_alien_forvaltning_stats.py # Calculates status counts
    │   │   └── calculate_top_lists.py     # Calculates all top 10 lists
    │   └── display.UI/                  # Subdirectory for UI display modules
    │       ├── __init__.py              # (Likely present or should be added)
    │       ├── display_main_metrics_grid.py # Displays the top metrics grid and date range
    │       └── display_status_section.py  # Displays status-based sections (RedList, Alien etc.)
    ├── figures_dashboard/             # (Assumed) Directory potentially for static figures or plots
    │   └── ...
    └── dashboard_project_info.md      # This documentation file
    # Note: __pycache__ directories are omitted for brevity.
```

## Workflow

The primary entry point for this section is `dashboard.py`, specifically the `display_dashboard(data)` function. This function is typically called from a higher-level Streamlit application script (e.g., `app.py`).

1.  **Input**: The `display_dashboard` function receives a pandas DataFrame (`data`) containing the processed observation data. This data is expected to have specific columns (e.g., 'Art', 'Antall Individer', 'Familie', 'Innsamler/Observatør', 'Kategori (Rødliste/Fremmedart)', various status columns like 'Prioriterte Arter', etc.).
2.  **Initialization**: It checks/initializes a Streamlit session state variable (`show_dashboard_top_lists`) used to toggle the visibility of detailed Top 10 lists.
3.  **Empty Data Check**: It verifies if the input DataFrame is empty. If so, it displays a warning and exits.
4.  **Calculation Orchestration**: It calls functions from the `utils_dashboard/calculations/` modules:
    *   `calculate_basic_metrics(data)`: Computes total observations, individuals, unique counts (species, families, observers), and the date range. Returns a dictionary.
    *   `calculate_all_status_counts(data)`: Computes counts for Red List categories, Alien Species categories, and other special status categories ('Prioriterte Arter', etc.). Returns a dictionary including the counts and the category lists/orders.
    *   `calculate_all_top_lists(data, top_n=10)`: Computes various Top 10 lists: by frequency (species, families, observers), by individual count (raw observations), and aggregated by category/status (species frequency and sum of individuals within Red List, Alien, Special Status categories). Returns a dictionary of pandas DataFrames.
5.  **Formatting Setup**: It gathers the formatting functions from `utils_dashboard/formatting.py` into a dictionary to pass to display functions.
6.  **Display Orchestration**: It sets up the main "Dashboard Oversikt" header and the "Topp 10" toggle button. It then calls functions from the `utils_dashboard/display.UI/` modules, passing the calculated data and formatting functions:
    *   `display_main_metrics_grid(...)`: Renders the 5-column grid showing basic metrics. Conditionally displays the simple frequency Top 10 lists (Species, Families, Observers) and the Top 10 individual observations list below their respective metrics based on the session state toggle.
    *   `display_all_status_sections(...)`: Renders the sections for Red List, Alien Species, and Special Status. Each section displays the relevant metrics per category/type. Conditionally displays the aggregated Top 10 species lists (frequency | sum individuals) below each metric based on the session state toggle, using the appropriate formatter from `formatting.py`.
    *   `display_date_range(...)`: Renders the 'Observasjonsperiode' section showing the first and last observation dates found.

## Setup

### Dependencies

This dashboard relies on the following Python libraries:

*   `streamlit`: For creating the web app interface and managing state.
*   `pandas`: For data manipulation within the calculation functions.

### Installation (using uv)

It is recommended to use `uv` for package management. Ensure `uv` is installed. Dependencies are likely shared with other parts of the project. If adding these specifically, run from the workspace root (`artsdata` directory):

```bash
# If not already added by other modules
uv add streamlit pandas
# To ensure all project dependencies are installed
uv sync
```

Alternatively, if using `pip` and `venv`:

```bash
# Ensure virtual environment is active
pip install streamlit pandas
```

## Usage

The `dashboard.py` script itself is not typically run directly. Instead, its `display_dashboard(data)` function is imported and called within a main Streamlit application script (e.g., `app.py` in the project root or `mapper_streamlit` directory).

Example call within `app.py`:

```python
import streamlit as st
import pandas as pd
from mapper_streamlit.landingsside.dashboard import display_dashboard

# --- Load Processed Data ---
# Assuming 'final_processed_data.csv' is the output from the databehandling pipeline
try:
    processed_data = pd.read_csv("path/to/your/final_processed_data.csv")
except FileNotFoundError:
    st.error("Processed data file not found.")
    st.stop() # Stop execution if data isn't available

# --- Display Dashboard Section ---
st.title("Artsdata Dashboard")
display_dashboard(processed_data)

# ... other Streamlit app components ...
```

To run the Streamlit application (assuming the main script is `app.py` in the root):

```bash
streamlit run app.py
```

## Configuration Notes

*   **Input Data Columns**: The calculation and display functions rely on specific column names being present in the input DataFrame `data`. These names (e.g., `Art`, `Antall Individer`, `Kategori (Rødliste/Fremmedart)`, `Prioriterte Arter`) are hardcoded within the utility functions in `utils_dashboard/`. Changes in the data processing pipeline affecting these column names will require updates here.
*   **Session State**: The visibility toggle for Top 10 lists uses `st.session_state['show_dashboard_top_lists']`.
*   **Constants**: Status categories (`REDLIST_CATEGORIES`, `ALIEN_CATEGORIES_LIST`, `SPECIAL_STATUS_COLS`) used for calculations and display ordering are defined as constants in `utils_dashboard/calculations/calculate_redlists_alien_forvaltning_stats.py` and `utils_dashboard/calculations/calculate_top_lists.py`.
*   **Top N**: The number of items shown in "Top" lists is hardcoded (default `top_n=10`) in the call to `calculate_all_top_lists` within `dashboard.py`.

## Current State & Future Improvements

*   **Refactored Structure**: The code has been refactored from a single large script into modular calculation, formatting, and display components, improving maintainability.
*   **Minimal Implementation**: Following initial development principles, the utility functions currently contain minimal functional logic. They generally lack comprehensive error handling, input validation, type hinting, extensive docstrings, and logging.
*   **Error Handling**: Adding `try...except` blocks (e.g., around accessing potentially missing dictionary keys or DataFrame columns, handling date/numeric conversion errors during calculation) would make the dashboard more robust.
*   **Input Validation**: Explicitly checking for the existence and potentially the types of required columns in the input DataFrame within the calculation functions would prevent runtime errors.
*   **Logging**: Implementing logging could help diagnose issues, especially during calculations.
*   **Type Hinting & Docstrings**: Adding type hints and comprehensive docstrings to all functions would improve code clarity, maintainability, and enable static analysis.
*   **Testing**: Adding unit tests (e.g., using `pytest`) for the calculation functions (with various sample DataFrames) and formatting functions would ensure correctness and prevent regressions. Testing Streamlit display components is more complex but could be considered.
*   **Performance**: For very large datasets, the performance of pandas operations in the calculation steps could be profiled and potentially optimized if needed.

# Streamlit Dashboard Documentation (`landingsside`)

## Purpose

This directory contains the Streamlit components responsible for generating and displaying the main summary dashboard for the species observation data. It takes processed data **with original column names** (expected output from the `databehandling` pipeline or data loading step) and presents key metrics, counts, top lists, and an interactive time-series figure in a web interface.

## Project Structure

```
mapper_streamlit/
└── landingsside/
    ├── dashboard.py                     # Main dashboard orchestration script
    ├── utils_dashboard/                 # Directory for dashboard utility modules
    │   ├── __init__.py
    │   ├── formatering_md_tekst.py      # Module for formatting data into markdown
    │   ├── calculations/                # Subdirectory for data calculation modules
    │   │   ├── __init__.py
    │   │   ├── calculate_basic_metrics.py # Calculates overall totals, uniques (uses original cols)
    │   │   ├── calculate_redlists_alien_forvaltning_stats.py # Calculates status counts (uses original cols)
    │   │   └── calculate_top_lists.py     # Calculates all top 10 lists (uses original cols)
    │   └── display_UI/                  # Subdirectory for UI display modules
    │       ├── __init__.py
    │       ├── display_main_metrics_grid.py # Displays the top metrics grid (expects display names)
    │       └── display_rødliste_fremmedarter_arter_av_forvaltningsinteresse.py # Displays status sections (expects display names)
    ├── figures_dashboard/             # Directory for figure generation modules
    │   ├── __init__.py
    │   ├── obs_periode_calculations.py  # Calculates yearly data (uses original cols)
    │   └── obs_periode_figur.py         # Creates the interactive observation period Plotly figure
    └── dashboard_project_info.md      # This documentation file
    # Note: __pycache__ directories are omitted for brevity.
```

## Workflow

The primary entry point for this section is `dashboard.py`, specifically the `display_dashboard(data, **original_col_kwargs)` function. This function is typically called from a higher-level Streamlit application script (e.g., `Oversikt.py`).

1.  **Input**: 
    *   The `display_dashboard` function receives a pandas DataFrame (`data`) containing the **original** observation data columns.
    *   It also receives several keyword arguments specifying the *actual original column names* in the DataFrame corresponding to key metrics (e.g., `original_art_col="preferredPopularName"`, `original_event_date_col="dateTimeCollected"`). See the function signature for all required column name parameters.
2.  **Initialization**: It checks/initializes a Streamlit session state variable (`show_dashboard_top_lists`) used to toggle the visibility of detailed Top 10 lists.
3.  **Empty Data Check**: It verifies if the input DataFrame is empty. If so, it displays a warning and exits.
4.  **Calculation Orchestration**: It calls functions from the `utils_dashboard/calculations/` and `figures_dashboard/` modules, passing the `data` DataFrame (with original names) and the specific *original column names* required by each function:
    *   `calculate_basic_metrics(data, individual_count_col=..., art_col=..., ...)`: Computes total observations, individuals, unique counts. Returns a dictionary. Date parsing is now more flexible (no fixed format string).
    *   `calculate_all_status_counts(data, category_col=..., alien_flag_col=..., original_special_status_cols=...)`: Computes counts for Red List, Alien Species, and other special status categories. Returns a dictionary.
    *   `calculate_all_top_lists(data, art_col=..., family_col=..., ...)`: Computes various Top 10 lists. Returns a dictionary (`raw_top_lists`) where DataFrames have *original* column names (or generic aggregate names).
    *   `calculate_yearly_metrics(data, date_col_name=..., individuals_col_name=...)`: Computes yearly sums and averages. Returns a DataFrame. Date parsing is now more flexible.
5.  **Prepare Top Lists for Display**: It takes the `raw_top_lists` dictionary and creates a new dictionary `display_top_lists`. It iterates through the DataFrames in `raw_top_lists`, copies them, and renames their columns to user-friendly *display names* using `get_display_name` (imported from `global_utils.column_mapping`).
6.  **Formatting Setup**: It gathers the formatting functions from `utils_dashboard/formatering_md_tekst.py` into a dictionary. These formatting functions expect DataFrames with *display names*.
7.  **Display Orchestration**:
    *   Sets up the main header and toggle button.
    *   Calls `display_main_metrics_grid(...)` passing `basic_metrics` and the *renamed* `display_top_lists`.
    *   Calls `display_all_status_sections(...)` passing `status_counts` and the *renamed* `display_top_lists`.
    *   **Observation Period Figure**:
        *   Adds subheader and multiselect widget (using display names for options).
        *   Maps selected display trace names back to actual column names in `yearly_metrics_data`.
        *   Calls `create_observation_period_figure(...)` passing `yearly_metrics_data` and the *actual column names* to plot.
        *   Displays the generated Plotly figure.
    *   Adds separators.

## Setup

### Dependencies

*   `streamlit`
*   `pandas`
*   `plotly`
*   Requires `global_utils/column_mapping.py` for internal renaming.

### Installation (using uv)

```bash
# If not already added
uv add streamlit pandas plotly
# Ensure all installed
uv sync
```

## Usage

The `display_dashboard` function is imported and called within a main Streamlit application script (e.g., `Oversikt.py`), passing the DataFrame with **original column names** and specifying the required original column name parameters.

Example call within `Oversikt.py`:

```python
# ... (load and prepare data as innlastet_data) ...
# --- Apply Filters ---
data_for_visning = apply_filters(innlastet_data) # Data still has ORIGINAL column names

# --- Define Actual Original Column Names ---
# (Get these from your data source or mapping definition)
actual_original_art_col = "preferredPopularName"
actual_original_family_col = "FamilieNavn"
actual_original_observer_col = "collector"
actual_original_individual_count_col = "individualCount"
actual_original_event_date_col = "dateTimeCollected"
actual_original_category_col = "category"
actual_original_alien_flag_col = "Fremmede arter"
actual_original_special_status_cols = [
    "Prioriterte arter", "Andre spesielt hensynskrevende arter", 
    "Ansvarsarter", "Spesielle okologiske former"
]

# --- Display Dashboard Section ---
st.title("Artsdata Dashboard")
# Pass data with ORIGINAL names + parameters mapping original names
display_dashboard(
    data_for_visning, # Pass data with ORIGINAL names
    original_art_col=actual_original_art_col,
    original_family_col=actual_original_family_col,
    original_observer_col=actual_original_observer_col,
    original_individual_count_col=actual_original_individual_count_col,
    original_event_date_col=actual_original_event_date_col,
    original_category_col=actual_original_category_col,
    original_alien_flag_col=actual_original_alien_flag_col,
    original_special_status_cols_list=actual_original_special_status_cols
)

# ... other Streamlit app components (may rename columns here if needed for other tables)...
```

To run the Streamlit application:

```bash
# From the workspace root
uv run streamlit run Oversikt.py
```

## Configuration Notes

*   **Input Data Columns**: `display_dashboard` now expects the input DataFrame to have **original** column names. It requires several keyword arguments specifying the *actual original names* for key columns (species, individuals, date, category, status flags, etc.). Calculation functions are called using these original names.
*   **Internal Renaming**: The `display_dashboard` function internally renames the columns of DataFrames returned by `calculate_all_top_lists` before passing them to the UI display/formatting functions (`display_main_metrics_grid`, `display_all_status_sections`, `formatering_md_tekst` functions). This relies on `global_utils.column_mapping.get_display_name`.
*   **Calculation Function Parameters**: All calculation functions (`calculate_basic_metrics`, `calculate_all_status_counts`, `calculate_all_top_lists`, `calculate_yearly_metrics`) now take original column names as parameters.
*   **Constants**: Status categories (`REDLIST_CATEGORIES`, `ALIEN_CATEGORIES_LIST`) remain defined in `calculate_redlists_alien_forvaltning_stats.py`. Original special status column names are now passed as a parameter list.
*   **Top N**: Still hardcoded (`top_n=10`) in the call to `calculate_all_top_lists` within `dashboard.py`.
*   **Figure Trace Selection**: Multiselect uses display names. Logic maps these back to actual column names (`Sum_Observations`, etc.) before calling `create_observation_period_figure`.
*   **Date Parsing**: `calculate_basic_metrics` and `calculate_yearly_metrics` now use more flexible date parsing (no fixed format string).

## Current State & Future Improvements

*   **Refactored Structure**: Remains modularized.
*   **Decoupled Input**: Dashboard logic now operates on original column names, reducing coupling with the calling script. Renaming for display is handled internally.
*   **Interactive Figure**: Unchanged.
*   **Error Handling**: Some added in `calculate_yearly_metrics`, but minimal elsewhere.
*   **Minimal Implementation**: Still largely lacks comprehensive type hinting, docstrings, logging.
*   **Input Validation**: Could add checks for the presence and types of the required original columns passed as parameters.
*   **Testing**: Tests have been updated to reflect the new function signatures.
*   **Performance**: `@st.cache_data` added to calculation functions.
*   **Linting**: Numerous linting errors still exist.

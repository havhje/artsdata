# Streamlit Dashboard Documentation (`landingsside`)

## Purpose

This directory contains the Streamlit components responsible for generating and displaying the main summary dashboard for the species observation data. It takes processed data (expected output from the `databehandling` pipeline) and presents key metrics, counts, top lists, and an interactive time-series figure in a web interface.

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
    │   │   ├── calculate_basic_metrics.py # Calculates overall totals, uniques
    │   │   ├── calculate_redlists_alien_forvaltning_stats.py # Calculates status counts
    │   │   └── calculate_top_lists.py     # Calculates all top 10 lists
    │   └── display_UI/                  # Subdirectory for UI display modules
    │       ├── __init__.py
    │       ├── display_main_metrics_grid.py # Displays the top metrics grid
    │       └── display_rødliste_fremmedarter_arter_av_forvaltningsinteresse.py # Displays status sections
    │       # Note: display_kartleggings_info.py removed or no longer used for date range
    ├── figures_dashboard/             # Directory for figure generation modules
    │   ├── __init__.py                  # (Potentially add if needed for imports)
    │   ├── obs_periode_calculations.py  # Calculates data needed for the observation period figure
    │   └── obs_periode_figur.py         # Creates the interactive observation period Plotly figure
    └── dashboard_project_info.md      # This documentation file
    # Note: __pycache__ directories are omitted for brevity.
```

## Workflow

The primary entry point for this section is `dashboard.py`, specifically the `display_dashboard(data)` function. This function is typically called from a higher-level Streamlit application script (e.g., `Oversikt.py`).

1.  **Input**: The `display_dashboard` function receives a pandas DataFrame (`data`) containing the **renamed** observation data (column names should match display names from `global_utils.column_mapping`).
2.  **Initialization**: It checks/initializes a Streamlit session state variable (`show_dashboard_top_lists`) used to toggle the visibility of detailed Top 10 lists.
3.  **Empty Data Check**: It verifies if the input DataFrame is empty. If so, it displays a warning and exits.
4.  **Calculation Orchestration**: It calls functions from the `utils_dashboard/calculations/` and `figures_dashboard/` modules:
    *   `calculate_basic_metrics(data)`: Computes total observations, individuals, unique counts (species, families, observers). Returns a dictionary. *(Note: Date range calculation might be redundant now)*.
    *   `calculate_all_status_counts(data)`: Computes counts for Red List categories, Alien Species categories, and other special status categories ('Prioriterte Arter', etc.). Returns a dictionary.
    *   `calculate_all_top_lists(data, top_n=10)`: Computes various Top 10 lists. Returns a dictionary.
    *   `calculate_yearly_metrics(data, date_col_name, individuals_col_name)`: Computes yearly sums of observations, individuals, and the average individuals per observation, using specified (renamed) column names. Returns a DataFrame.
5.  **Formatting Setup**: It gathers the formatting functions from `utils_dashboard/formatering_md_tekst.py` into a dictionary.
6.  **Display Orchestration**:
    *   Sets up the main "Kartleggingsstatestikk" header and the "Topp 10" toggle button.
    *   Calls `display_main_metrics_grid(...)` to render the 5-column grid with basic metrics and conditional Top 10 lists.
    *   Calls `display_all_status_sections(...)` to render the sections for Red List, Alien Species, and Special Status with their metrics and conditional Top 10 lists.
    *   **Observation Period Figure**:
        *   Adds a subheader "Observasjoner over tid".
        *   Displays an `st.multiselect` widget allowing users to choose which traces ('Antall Observasjoner', 'Antall Individer', 'Gj.snitt Individer/Observasjon') to show in the figure.
        *   If the yearly metrics data is not empty and at least one trace is selected, it calls `create_observation_period_figure(...)` from `figures_dashboard/obs_periode_figur.py`, passing the yearly data and the list of selected traces.
        *   Displays the generated Plotly figure using `st.plotly_chart`.
    *   Adds a final separator.

## Setup

### Dependencies

This dashboard relies on the following Python libraries:

*   `streamlit`: For creating the web app interface and managing state.
*   `pandas`: For data manipulation within the calculation functions.
*   `plotly`: For generating the interactive observation period figure.

### Installation (using uv)

It is recommended to use `uv` for package management. Ensure `uv` is installed. Dependencies are likely shared with other parts of the project. If adding these specifically, run from the workspace root (`artsdata` directory):

```bash
# If not already added by other modules
uv add streamlit pandas plotly
# To ensure all project dependencies are installed
uv sync
```

Alternatively, if using `pip` and `venv`:

```bash
# Ensure virtual environment is active
pip install streamlit pandas plotly
```

## Usage

The `dashboard.py` script itself is not typically run directly. Instead, its `display_dashboard(data)` function is imported and called within a main Streamlit application script (e.g., `Oversikt.py` in the project root), passing the **renamed** DataFrame.

Example call within `Oversikt.py`:

```python
# ... (load and prepare data as innlastet_data) ...

# --- Apply Filters ---
data_for_visning = apply_filters(innlastet_data) # Assuming this returns data with ORIGINAL column names

# --- Prepare Data for Dashboard ---
data_for_dashboard = data_for_visning.copy()
# Rename columns JUST before calling the dashboard
data_for_dashboard.columns = [get_display_name(col) for col in data_for_dashboard.columns]

# --- Display Dashboard Section ---
st.title("Artsdata Dashboard")
display_dashboard(data_for_dashboard) # Pass the RENAMED data

# ... other Streamlit app components ...
```

To run the Streamlit application:

```bash
# From the workspace root
uv run streamlit run Oversikt.py
# Or if using venv
# source .venv/bin/activate
# streamlit run Oversikt.py
```

## Configuration Notes

*   **Input Data Columns**: Calculation and display functions called within `display_dashboard` generally expect **renamed** column names (e.g., `Art`, `Antall Individer`, `Innsamlingsdato/-tid`, `Kategori (Rødliste/Fremmedart)`, `Prioriterte Arter`) as defined in `global_utils/column_mapping.py`. Ensure the renaming step occurs in the calling script (`Oversikt.py`) before passing the data. The `calculate_yearly_metrics` function specifically takes the renamed date and individual column names as arguments.
*   **Session State**: The visibility toggle for Top 10 lists uses `st.session_state['show_dashboard_top_lists']`.
*   **Constants**: Status categories (`REDLIST_CATEGORIES`, `ALIEN_CATEGORIES_LIST`, `SPECIAL_STATUS_COLS`) used for calculations and display ordering are defined in the respective calculation modules.
*   **Top N**: The number of items shown in "Top" lists is hardcoded (default `top_n=10`) in the call to `calculate_all_top_lists`.
*   **Figure Trace Selection**: The multiselect widget for the observation period figure defaults to showing 'Antall Observasjoner' and 'Antall Individer'. The available trace names are hardcoded in `dashboard.py`.
*   **List Formatting**: The format of the text-based top lists is controlled by functions in `formatering_md_tekst.py`.

## Current State & Future Improvements

*   **Refactored Structure**: The code is modularized into calculation, formatting, display, and figure generation components.
*   **Interactive Figure**: Added an interactive Plotly figure showing yearly trends, replacing the static date range display. Users can select which metrics to plot.
*   **Error Handling**: Robustness was improved in `calculate_yearly_metrics` by adding `try...except` blocks and checks for required columns, returning empty DataFrames on failure to prevent crashes. Similar handling could be added to other calculation functions.
*   **Minimal Implementation**: Utility functions still largely follow minimal functional logic, lacking comprehensive type hinting, extensive docstrings, and widespread logging beyond the added error logging in `calculate_yearly_metrics`.
*   **Input Validation**: Could add more explicit checks for expected DataFrame structures and column types within calculation functions.
*   **Logging**: Could expand logging for better debugging and tracing data flow.
*   **Type Hinting & Docstrings**: Adding these would improve code clarity and maintainability.
*   **Testing**: Unit tests for calculation functions (especially `calculate_yearly_metrics`) are recommended.
*   **Performance**: Consider performance for very large datasets.
*   **Linting**: Numerous linting errors still exist and should be addressed.
*   **Figure Customization**: The observation period figure could be further customized (e.g., tooltips, colors, secondary y-axis options if desired later).

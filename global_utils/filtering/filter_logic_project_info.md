# Filtering Utilities Documentation (`global_utils/filtering`)

## Purpose

This sub-package within `global_utils` contains modules dedicated to handling data filtering for the Artsdata Streamlit application. It separates the concerns of defining filter constants, creating the user interface (UI) widgets, and applying the filtering logic to the data.

## Package Structure

```
filtering/
├── __init__.py                # Makes the directory a Python package
├── filter_constants.py      # Defines constants used by filter UI and logic
├── filter_logic.py          # Applies filter logic to the data based on session state
├── filter_ui.py             # Creates filter widgets in the Streamlit sidebar
└── filter_logic_project_info.md # This documentation file
```
*(Note: `__init__.py` should be added if not present)*

## Modules

### 1. `filter_constants.py`

*   **Purpose:** Defines constants used by both the filter UI creation and filter application logic.
*   **Key Components:**
    *   `REDLIST_CODES` (list): Codes representing Red List categories.
    *   `ALIEN_CODES` (list): Codes representing Alien Species risk categories.
    *   `SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL` (dict): Maps user-facing labels for special management statuses to their corresponding original column names in the data.
*   **Usage:** Imported by `filter_ui.py` and `filter_logic.py`.

### 2. `filter_ui.py`

*   **Purpose:** Handles the creation of filter widgets in the Streamlit sidebar.
*   **Key Components:**
    *   `display_filter_widgets(data)` (function):
        *   Takes the initial (unfiltered) DataFrame (`data`) as input.
        *   Creates various filter widgets in the `st.sidebar` (text search, taxonomy, status, date range).
        *   Uses a helper `_display_multiselect` to reduce repetition for standard multiselect filters.
        *   Dynamically populates filter options based on values present in the input `data`.
        *   Links widgets to `st.session_state` using unique `key` arguments (e.g., `filter_familie`, `filter_start_date`).
    *   `_display_multiselect(data, original_col_name, filter_key, display_label, options_filter_list=None)` (helper function): Creates a standard multiselect widget, handling column checks, unique value retrieval, optional pre-filtering of options, and display logic.
*   **Usage:** Imported and called by pages like `Oversikt.py` (or other main application pages) to display the sidebar UI. Requires `data` to populate options.

### 3. `filter_logic.py`

*   **Purpose:** Applies the selected filter criteria (stored in session state) to the data.
*   **Key Components:**
    *   `apply_filters(data)` (function):
        *   Takes a DataFrame (`data`) as input.
        *   Reads the current selections for each filter from `st.session_state`.
        *   Uses a helper `_apply_multiselect_filter` to reduce repetition for standard `.isin()` filters.
        *   Applies filters sequentially (Taxonomy, Status, Date Range, Text Search).
        *   Handles the specific logic for combined special status filtering and date range comparison.
        *   Returns the filtered DataFrame.
    *   `_apply_multiselect_filter(filtered_data, filter_key, original_col_name)` (helper function): Applies a standard `.isin()` filter based on session state for a given key and column.
*   **Usage:** Imported and called by pages like `Oversikt.py` (or other main application pages) after displaying widgets to get the filtered data for display.

## Dependencies

*   `streamlit`: For UI elements and session state access.
*   `pandas`: For DataFrame operations.

## Integration with Other `global_utils` Modules

*   **`session_state_manager.py`:** The filter keys used in `filter_ui.py` (e.g., `filter_familie`) **must** be listed in `PERSISTENT_FILTER_KEYS` within `session_state_manager.py` to ensure filter selections persist across pages.
*   **`column_mapping.py`:** While the filtering logic operates on the *original* data column names, the rest of the application might use `column_mapping.py` to get user-friendly display names *after* filtering.

## Usage Example (in a Streamlit page like `Oversikt.py`)

```python
# At the top of the page script
import streamlit as st
import pandas as pd
from global_utils.session_state_manager import initialize_and_persist_filters
from global_utils.filtering.filter_ui import display_filter_widgets
from global_utils.filtering.filter_logic import apply_filters
# Potentially: from global_utils.column_mapping import get_display_name

# --- Initialize Session State --- 
initialize_and_persist_filters() # Ensures filter state persists

# --- Load Data --- 
# @st.cache_data # Recommended for performance
def load_data(filepath):
    # ... logic to load data into a pandas DataFrame ...
    return pd.read_csv(filepath) # Example

df_original = load_data("path/to/your/data.csv")

# --- Display Filters --- 
st.sidebar.title("Data Filters")
display_filter_widgets(df_original) # Pass original data to populate filter options

# --- Apply Filters --- 
df_filtered = apply_filters(df_original) # Apply selections from session state

# --- Display Filtered Data --- 
st.header("Filtered Data")
st.dataframe(df_filtered) # Display the result

# You might rename columns for display here using column_mapping
# display_df = df_filtered.rename(columns=get_display_name) # Example
# st.dataframe(display_df)
```

## Current State & Future Improvements

*   **Refactored Core:** Filter UI and logic are separated. Helper functions reduce repetition.
*   **Minimal Implementation:** Modules lack detailed docstrings, type hints, extensive error handling (e.g., for invalid data types during filtering), and logging.
*   **Testing:** No unit tests currently exist.
*   **Linting:** Likely requires linting fixes for style consistency.

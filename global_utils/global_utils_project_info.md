# Global Utilities Documentation (`global_utils`)

## Purpose

This directory houses Python modules containing utility functions and configurations shared across different parts of the Artsdata Streamlit application. The primary goal is to centralize common functionalities like data filtering UI and logic, column name mapping, constants, and session state management for filters, promoting code reuse and maintainability.

## Project Structure

```
global_utils/
├── __init__.py
├── column_mapping.py            # Maps original data column names to display names
├── filter_constants.py          # Defines constants used by filter UI and logic
├── filter_logic.py              # Applies filter logic to the data based on session state
├── filter_ui.py                 # Creates filter widgets in the Streamlit sidebar
├── session_state_manager.py     # Manages persistent session state for filters
└── global_utils_project_info.md # This documentation file
```

## Modules

### 1. `column_mapping.py`

*   **Purpose:** Provides a centralized mapping from technical or source-specific column names (as found in the input CSV files) to more user-friendly Norwegian display names used in the application UI (tables, dashboards).
*   **Key Components:**
    *   `COLUMN_NAME_MAPPING` (dict): Stores the mapping from original names (keys) to display names (values).
    *   `get_display_name(original_name)` (function): Takes an original column name and returns the corresponding display name from the mapping, or the original name itself if no mapping exists.
*   **Usage:** Imported by modules like `Oversikt.py` and dashboard components to rename DataFrame columns before displaying data to the user.

### 2. `filter_constants.py`

*   **Purpose:** Defines constants used by both the filter UI creation and filter application logic.
*   **Key Components:**
    *   `REDLIST_CODES` (list): Codes representing Red List categories.
    *   `ALIEN_CODES` (list): Codes representing Alien Species risk categories.
    *   `SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL` (dict): Maps user-facing labels for special management statuses to their corresponding original column names in the data.
*   **Usage:** Imported by `filter_ui.py` and `filter_logic.py`.

### 3. `filter_ui.py`

*   **Purpose:** Handles the creation of filter widgets in the Streamlit sidebar.
*   **Key Components:**
    *   `display_filter_widgets(data)` (function):
        *   Takes the initial (unfiltered) DataFrame (`data`) as input.
        *   Creates various filter widgets in the `st.sidebar` (text search, taxonomy, status, date range).
        *   Uses a helper `_display_multiselect` to reduce repetition for standard multiselect filters.
        *   Dynamically populates filter options based on values present in the input `data`.
        *   Links widgets to `st.session_state` using unique `key` arguments (e.g., `filter_familie`, `filter_start_date`).
    *   `_display_multiselect(data, original_col_name, filter_key, display_label, options_filter_list=None)` (helper function): Creates a standard multiselect widget, handling column checks, unique value retrieval, optional pre-filtering of options, and display logic.
*   **Usage:** Imported and called by pages like `Oversikt.py` to display the sidebar UI.

### 4. `filter_logic.py`

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
*   **Usage:** Imported and called by pages like `Oversikt.py` after displaying widgets to get the filtered data for display.

### 5. `session_state_manager.py`

*   **Purpose:** Ensures that user selections in the filter widgets persist even when navigating between different pages of the multi-page Streamlit application.
*   **Key Components:**
    *   `PERSISTENT_FILTER_KEYS` (list): A list of all `st.session_state` keys used by the filter widgets in `filter_ui.py`.
    *   `initialize_and_persist_filters()` (function):
        *   Should be called at the **beginning** of each page script.
        *   Initializes each key in `st.session_state` with an appropriate default if it doesn't exist.
        *   Re-assigns the session state variable to itself to prevent widget state cleanup.
*   **Usage:** The `initialize_and_persist_filters()` function is called once at the start of `Oversikt.py` and should be called similarly in any other page script.

## Dependencies

*   `streamlit`: For UI elements and session state management.
*   `pandas`: For DataFrame operations.

## Usage Integration

These modules are designed to work together:

1.  A main page script (e.g., `Oversikt.py`) imports `initialize_and_persist_filters`, `display_filter_widgets` (from `filter_ui`), `apply_filters` (from `filter_logic`), and `get_display_name`.
2.  `initialize_and_persist_filters()` is called first.
3.  Data is loaded.
4.  `display_filter_widgets()` is called with the loaded data.
5.  `apply_filters()` is called with the loaded data.
6.  `get_display_name()` is used to rename columns of the filtered data before display.

## Configuration Notes

*   **Filter Keys:** Consistency between keys in `filter_ui.py` and `PERSISTENT_FILTER_KEYS` in `session_state_manager.py` is crucial.
*   **Column Names:** `filter_ui.py` and `filter_logic.py` rely on *original* column names. `column_mapping.py` provides display names.
*   **Status Codes/Mappings:** Constants in `filter_constants.py` drive status filter options/logic.

## Current State & Future Improvements

*   **Refactored Core:** Filter UI and logic are now separated for better modularity. Helper functions reduce some repetition.
*   **Data-Driven Filters:** Most filter options are dynamically generated based on loaded data.
*   **Minimal Implementation:** Modules still generally lack detailed docstrings, type hints, extensive error handling, and logging.
*   **Linting:** Linting errors (formatting, etc.) likely still exist.
*   **Optimization:** Date conversion in `filter_logic.py` could potentially be optimized.
*   **Testing:** No unit tests currently exist.

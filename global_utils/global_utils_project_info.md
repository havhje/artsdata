# Global Utilities Documentation (`global_utils`)

## Purpose

This directory houses Python modules containing utility functions and configurations shared across different parts of the Artsdata Streamlit application. The primary goal is to centralize common functionalities like data filtering UI and logic, column name mapping, and session state management for filters, promoting code reuse and maintainability.

## Project Structure

```
global_utils/
├── __init__.py
├── column_mapping.py            # Maps original data column names to display names
├── filter.py                    # Creates filter widgets and applies filter logic
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

### 2. `filter.py`

*   **Purpose:** Handles the creation of filter widgets in the Streamlit sidebar and applies the selected filter criteria to the data.
*   **Key Components:**
    *   `display_filter_widgets(data)` (function):
        *   Takes the initial (unfiltered) DataFrame (`data`) as input.
        *   Creates various filter widgets in the `st.sidebar`.
        *   Includes a general text search (`st.text_input`).
        *   Uses expanders (`st.expander`) to group filters (Taksonomi, Status, Tidsperiode).
        *   Dynamically populates filter options (e.g., for `st.multiselect`) based *only* on values present in the input `data` for most filters (Taxonomy, Red List, Alien Species, Special Status).
        *   Sets `min_value` and `max_value` for date filters based on the data range.
        *   Links widgets to `st.session_state` using unique `key` arguments (e.g., `filter_familie`, `filter_start_date`).
    *   `apply_filters(data)` (function):
        *   Takes a DataFrame (`data`) as input (typically the initially loaded data).
        *   Reads the current selections for each filter from `st.session_state` using the defined keys.
        *   Applies filters sequentially if a selection has been made for that filter.
        *   Uses pandas boolean indexing (`.isin()`, date comparisons, `.str.contains()`) to filter the DataFrame based on original column names.
        *   Handles the combined logic for the "Special Category" filter (checking multiple 'Yes'/'No' columns).
        *   Applies the general text search across all string columns as the final step.
        *   Returns the filtered DataFrame.
    *   **Constants:** Defines `REDLIST_CODES`, `ALIEN_CODES`, `SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL` used for populating and applying status filters.
*   **Usage:** Imported and called by `Oversikt.py` to display the sidebar and filter the data before it's passed to display components like the dashboard or tables.

### 3. `session_state_manager.py`

*   **Purpose:** Ensures that user selections in the filter widgets persist even when navigating between different pages of the multi-page Streamlit application.
*   **Key Components:**
    *   `PERSISTENT_FILTER_KEYS` (list): A list of all `st.session_state` keys used by the filter widgets in `filter.py`.
    *   `initialize_and_persist_filters()` (function):
        *   Should be called at the **beginning** of each page script (like `Oversikt.py` and other files in the `pages/` directory).
        *   Iterates through `PERSISTENT_FILTER_KEYS`.
        *   Initializes each key in `st.session_state` with an appropriate default (e.g., `[]` for multiselect, `""` for text, `None` for dates) *only if* the key doesn't already exist.
        *   Re-assigns the session state variable to itself (`st.session_state[key] = st.session_state[key]`) to prevent Streamlit's default widget state cleanup from removing the value when the widget isn't rendered on the current page.
*   **Usage:** The `initialize_and_persist_filters()` function is called once at the start of `Oversikt.py` and should be called similarly in any other page script added to the `pages/` directory.

## Dependencies

*   `streamlit`: For UI elements and session state management.
*   `pandas`: For DataFrame operations (checking columns, filtering, date conversion).

## Usage Integration

These modules are designed to work together:

1.  A main page script (e.g., `Oversikt.py`) imports `initialize_and_persist_filters`, `display_filter_widgets`, `apply_filters`, and `get_display_name`.
2.  `initialize_and_persist_filters()` is called first to ensure session state is ready.
3.  Data is loaded.
4.  `display_filter_widgets()` is called with the loaded data to render the sidebar UI.
5.  `apply_filters()` is called with the loaded data to get the filtered dataset based on current session state values.
6.  `get_display_name()` is used to rename columns of the filtered data before passing it to display functions (like `display_dashboard`).

## Configuration Notes

*   **Filter Keys:** Consistency between the keys used in `filter.py` and the `PERSISTENT_FILTER_KEYS` list in `session_state_manager.py` is crucial.
*   **Column Names:** `filter.py` relies on the *original* column names from the data. `column_mapping.py` provides the translation to display names.
*   **Status Codes/Mappings:** Predefined lists and dictionaries in `filter.py` determine the options and logic for status filters.

## Current State & Future Improvements

*   **Functional Core:** Provides essential column mapping, filtering UI/logic, and state persistence.
*   **Data-Driven Filters:** Most filter options are now dynamically generated based on the loaded data.
*   **Minimal Implementation:** Modules generally lack detailed docstrings, type hints beyond basic ones, extensive error handling (e.g., for unexpected data types in filters), and logging.
*   **Linting:** Significant number of linting errors (mostly formatting, line length, comments) exist across the files.
*   **Optimization:** Date conversion happens multiple times in `filter.py`; could be optimized by performing it once after data loading.
*   **Testing:** No unit tests currently exist for these utility functions.

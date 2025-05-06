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
*   **Usage:** Imported by modules like `Oversikt.py` to rename DataFrame columns before displaying data directly in tables. Also used internally by components like `mapper_streamlit/landingsside/dashboard.py` to rename calculated results (e.g., top lists) before passing them to formatting or UI display functions.

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
    *   `display_filter_widgets(data)` (function): Takes initial data, creates widgets linked to session state.
    *   `_display_multiselect(...)` (helper function): Creates standard multiselect widget.
*   **Usage:** Imported and called by pages like `Oversikt.py`.

### 4. `filter_logic.py`

*   **Purpose:** Applies the selected filter criteria (stored in session state) to the data.
*   **Key Components:**
    *   `apply_filters(data)` (function): Takes data, reads session state, applies filters, returns filtered data.
    *   `_apply_multiselect_filter(...)` (helper function): Applies `.isin()` filter.
*   **Usage:** Imported and called by pages like `Oversikt.py`.

### 5. `session_state_manager.py`

*   **Purpose:** Ensures filter selections persist across pages.
*   **Key Components:**
    *   `PERSISTENT_FILTER_KEYS` (list): Session state keys used by filters.
    *   `initialize_and_persist_filters()` (function): Initializes/persists filter keys in session state.
*   **Usage:** `initialize_and_persist_filters()` called at the start of each page script.

## Dependencies

*   `streamlit`: For UI elements and session state management.
*   `pandas`: For DataFrame operations.

## Usage Integration

These modules are designed to work together:

1.  A main page script (e.g., `Oversikt.py`) imports `initialize_and_persist_filters`, `display_filter_widgets`, `apply_filters`, and potentially `get_display_name`.
2.  `initialize_and_persist_filters()` is called first.
3.  Data is loaded (with original column names).
4.  `display_filter_widgets()` is called with the loaded data.
5.  `apply_filters()` is called with the loaded data to get filtered data (still with original column names).
6.  **Displaying Data:**
    *   For direct display in tables on the main page (like in `Oversikt.py`), `get_display_name()` is typically used to rename columns of the filtered data *before* passing to `st.dataframe`.
    *   For complex components like the dashboard (`mapper_streamlit/landingsside/dashboard.py`), the filtered data (with *original* names) is passed along with parameters specifying the relevant original column names. The component itself then uses `get_display_name` internally if needed before final rendering.

## Configuration Notes

*   **Filter Keys:** Consistency between keys in `filter_ui.py` and `PERSISTENT_FILTER_KEYS` is crucial.
*   **Column Names:** `filter_ui.py` and `filter_logic.py` operate on *original* column names. `column_mapping.py` provides display names used for UI rendering.
*   **Status Codes/Mappings:** Constants in `filter_constants.py` drive status filter options/logic.

## Current State & Future Improvements

*   **Refactored Core:** Filter UI and logic are separated.
*   **Data-Driven Filters:** Most filter options are dynamic.
*   **Minimal Implementation:** Lack detailed docstrings, type hints, extensive error handling, logging.
*   **Linting:** Errors likely exist.
*   **Optimization:** Date conversion in filter logic could be reviewed.
*   **Testing:** No unit tests currently exist.

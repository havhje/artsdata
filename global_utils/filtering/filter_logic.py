##### Imports #####
import streamlit as st # Import Streamlit for session state access
import pandas as pd # Import pandas for DataFrame operations
from .filter_constants import SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL # Import constants from the dedicated file

##### Helper Functions #####

# --- Function: _apply_multiselect_filter ---
# Applies a filter to the DataFrame based on selected values from a multiselect widget.
# Reads the selection from st.session_state using the provided filter_key.
# Filters the specified original_col_name in the DataFrame.
# Returns the filtered DataFrame.
def _apply_multiselect_filter(filtered_data, filter_key, original_col_name):
    # Check if the filter key exists in session state and has a non-empty list selected.
    if filter_key in st.session_state and st.session_state[filter_key]:
        selected_values = st.session_state[filter_key] # Retrieve the list of selected values.
        # Apply the filter only if the target column exists in the DataFrame.
        if original_col_name in filtered_data.columns:
            # Use .isin() to filter rows where the column value is in the selected list.
            filtered_data = filtered_data[filtered_data[original_col_name].isin(selected_values)] # Modify filtered_data in place with the result.
    return filtered_data # Return the potentially filtered DataFrame.

##### Main Logic Function #####

# --- Function: apply_filters --- 
# Filters the DataFrame based on values stored in st.session_state by the UI widgets.
# Assumes 'data' is a pandas DataFrame and session state keys match those used in filter_ui.py.
def apply_filters(data):
    # Return the original DataFrame immediately if it's empty.
    if data.empty:
        return data # No filtering needed on empty data.

    filtered_data = data.copy() # Start with a copy to avoid modifying the original DataFrame.

    # --- Apply Taxonomic Filters --- # Use helper for Familie, Orden, Art
    filtered_data = _apply_multiselect_filter(filtered_data, 'filter_familie', "FamilieNavn") # Apply Familie filter.
    filtered_data = _apply_multiselect_filter(filtered_data, 'filter_orden', "OrdenNavn") # Apply Orden filter.
    filtered_data = _apply_multiselect_filter(filtered_data, 'filter_art', "preferredPopularName") # Apply Art filter.

    # --- Apply Status Filters --- # Apply filters related to species status.
    category_col = "category" # Original column for Red List / Alien status.

    # --- Apply Red List Filter --- # Use helper.
    filtered_data = _apply_multiselect_filter(filtered_data, 'filter_redlist_category', category_col) # Apply Red List filter.

    # --- Apply Special Category Filter --- # Custom logic required.
    filter_key_special = 'filter_special_category' # Session state key.
    # Check if the filter key exists and has selections.
    if filter_key_special in st.session_state and st.session_state[filter_key_special]:
        selected_labels = st.session_state[filter_key_special] # Get selected display labels.
        # Combine conditions: row must have 'Yes' in AT LEAST ONE selected special status column.
        combined_condition = pd.Series(False, index=filtered_data.index) # Initialize a Series of False values.
        for label in selected_labels: # Iterate through the selected labels.
            original_col_special = SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL.get(label) # Get the corresponding original column name.
            # Check if the mapping exists and the column is present in the data.
            if original_col_special and original_col_special in filtered_data.columns:
                # Update the combined condition: OR logic ensures row is kept if *any* selected column is 'Yes'.
                combined_condition = combined_condition | (filtered_data[original_col_special] == 'Yes') # Combine with previous conditions using logical OR.
        filtered_data = filtered_data[combined_condition] # Apply the final combined condition mask.

    # --- Apply Alien Species Filter --- # Use helper.
    filtered_data = _apply_multiselect_filter(filtered_data, 'filter_alien_category', category_col) # Apply Alien Species filter.

    # --- Apply Date Range Filter --- # Filter based on selected start and end dates.
    date_col = "dateTimeCollected" # Original column name for date/time.
    start_key = 'filter_start_date' # Session state key for start date.
    end_key = 'filter_end_date'   # Session state key for end date.

    # Get start and end dates from session state, defaulting to None if not present.
    start_date = st.session_state.get(start_key)
    end_date = st.session_state.get(end_key)

    # Proceed only if both dates are selected (not None) and the date column exists.
    if start_date is not None and end_date is not None and date_col in filtered_data.columns:
        # Basic validation: Ensure start date is not after end date.
        if start_date <= end_date:
            # Convert the relevant column to datetime objects, specifying the expected format and coercing errors.
            # This prevents the UserWarning and ensures correct parsing for DD.MM.YYYY format.
            date_col_dt = pd.to_datetime(filtered_data[date_col], format='%d.%m.%Y %H:%M:%S', errors='coerce')

            # Create a boolean mask for rows with valid dates within the selected range.
            date_mask = (
                date_col_dt.notna() & # Ensure the date is valid (not NaT).
                (date_col_dt.dt.date >= start_date) & # Check if the date is on or after the start date.
                (date_col_dt.dt.date <= end_date) # Check if the date is on or before the end date.
            )
            filtered_data = filtered_data[date_mask] # Apply the date range mask.
        # else: # Optional: Could add a warning if start date is after end date, but omitted for minimal approach.
            # st.sidebar.warning("Startdato kan ikke være etter sluttdato.")

    # --- Apply General Text Search LAST --- # Apply the free-text search filter.
    filter_key_text = 'filter_general_text' # Session state key for text search.
    search_text = st.session_state.get(filter_key_text, "").strip().lower() # Get search text, default empty, strip whitespace, convert to lower.

    # Proceed only if search text is provided.
    if search_text:
        # Select columns with string-like data (object dtype typically holds strings).
        string_columns = filtered_data.select_dtypes(include='object').columns

        # Check if there are any string columns to search in.
        if not string_columns.empty:
            # Split search text into terms (words) for potentially more precise matching.
            search_terms = search_text.split()

            # Initialize final mask to include all rows initially.
            final_mask = pd.Series(True, index=filtered_data.index) # Start with a mask where all rows are True.

            # Apply each search term using AND logic (all terms must match).
            for term in search_terms:
                # Mask for the current term: True if term found (case-insensitive) in ANY string column for the row.
                term_mask = filtered_data[string_columns].apply(
                    lambda row: row.astype(str).str.contains(term, case=False, na=False).any(), # Check each cell in the row (converted to string).
                    axis=1 # Apply function row-wise.
                )
                # Combine the current term's mask with the overall mask using logical AND.
                final_mask &= term_mask # Row must match *all* terms.

            # Apply the final combined mask to the DataFrame.
            filtered_data = filtered_data[final_mask]

    return filtered_data # Return the fully filtered DataFrame. 
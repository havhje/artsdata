##### Imports #####
import streamlit as st # Import Streamlit for UI elements
import pandas as pd # Import pandas for DataFrame operations
from .filter_constants import REDLIST_CODES, ALIEN_CODES, SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL # Import constants from the dedicated file. Relative import used.

##### Helper Functions #####

# --- Function: _display_multiselect --- 
# Displays a multiselect widget if a column exists and has unique values.
# Reduces repetition in the main display function.
# Assumes 'data' is a pandas DataFrame.
def _display_multiselect(data, original_col_name, filter_key, display_label, options_filter_list=None):
    # Check if the primary column for options exists in the DataFrame.
    if original_col_name in data.columns:
        unique_values = data[original_col_name].dropna().unique() # Get unique non-null values from the column.
        
        # If a specific list is provided to filter the options (e.g., REDLIST_CODES), use it.
        if options_filter_list is not None: 
            options = sorted([val for val in unique_values if val in options_filter_list]) # Filter unique values against the provided list and sort.
        else:
            options = sorted(list(unique_values)) # Otherwise, use all unique values and sort.
        
        # Display the multiselect widget only if there are options to show.
        if options:
            st.multiselect(
                display_label, # The user-facing label for the widget.
                options=options, # The list of choices for the user.
                key=filter_key # The key to store the selected value(s) in st.session_state.
            )
        # If there are no options after filtering/checking, display a caption.
        else:
            st.caption(f"Ingen relevante '{display_label}' funnet.") # Inform user if no relevant options available.
    # If the column itself doesn't exist in the data, display a caption.
    else:
        st.caption(f"Data for '{display_label}' (kolonne: {original_col_name}) mangler.") # Inform user if the required column is missing.

##### Main UI Function #####

# --- Function: display_filter_widgets --- 
# Creates Streamlit widgets for filtering the data in the sidebar.
# Assumes 'data' is a pandas DataFrame containing filterable columns.
# Stores selected filter values in st.session_state using specified keys.
def display_filter_widgets(data):
    
    st.sidebar.header("Filtreringsvalg") # Add a header to the sidebar section.

    # --- General Text Search --- # Text input for general search across string columns.
    filter_key_text = 'filter_general_text' # Session state key for the text input.
    st.sidebar.text_input(
        "Generelt Tekstsøk", # Label for the text input widget.
        key=filter_key_text, # Link widget to session state.
        placeholder="Søk i alle tekstfelt..." # Placeholder text guides the user.
    )

    # --- Taxonomy Expander --- # Group taxonomic filters in an expander.
    with st.sidebar.expander("Taksonomi", expanded=False): # Expander starts collapsed.
        # Use the helper function for Familie, Orden, and Art filters.
        _display_multiselect(data, "FamilieNavn", 'filter_familie', "Familie") # Call helper for Familie.
        _display_multiselect(data, "OrdenNavn", 'filter_orden', "Orden") # Call helper for Orden.
        _display_multiselect(data, "preferredPopularName", 'filter_art', "Art") # Call helper for Art.

    # --- Status Expander --- # Group status-related filters.
    with st.sidebar.expander("Status", expanded=False): # Expander starts collapsed.
        category_col = "category" # Define the shared original column name for Red List / Alien status.

        # --- Red List Filter --- # Use helper, filtering options by REDLIST_CODES.
        _display_multiselect(data, category_col, 'filter_redlist_category', "Rødlistekategori", options_filter_list=REDLIST_CODES)

        # --- Special Category Filter --- # Custom logic needed here as it checks multiple columns.
        filter_key_special = 'filter_special_category' # Session state key.
        display_label_special = "Arter av nasjonal forvaltningsstatus" # Display label.
        options_special = [] # Initialize empty list to store available special status labels.
        # Check which special status columns exist AND have at least one 'Yes' value.
        for label, original_col in SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL.items(): # Iterate through the mapping.
            if original_col in data.columns and (data[original_col] == 'Yes').any(): # Check column exists and has 'Yes'.
                options_special.append(label) # Add the user-friendly label if relevant data exists.

        # Display multiselect only if relevant special statuses were found.
        if options_special:
            st.multiselect(
                display_label_special, # Widget label.
                options=sorted(options_special), # Provide the sorted list of found statuses.
                key=filter_key_special # Link to session state.
            )
        else:
            st.caption(f"Ingen relevante '{display_label_special}' funnet.") # Inform user if no special statuses found.

        # --- Alien Species Filter --- # Use helper, filtering options by ALIEN_CODES.
        _display_multiselect(data, category_col, 'filter_alien_category', "Fremmedartrisiko", options_filter_list=ALIEN_CODES)

    # --- Date Range Expander --- # Group date range filters.
    with st.sidebar.expander("Tidsperiode", expanded=False): # Expander starts collapsed.
        date_col = "dateTimeCollected" # Original column name for date/time information.
        start_key = 'filter_start_date' # Session state key for start date.
        end_key = 'filter_end_date'   # Session state key for end date.
        start_label = "Startdato"    # Display label for start date input.
        end_label = "Sluttdato"      # Display label for end date input.

        # Check if the date column exists in the DataFrame.
        if date_col in data.columns:
            # Attempt to convert the column to datetime objects, coercing errors to NaT (Not a Time).
            date_series = pd.to_datetime(data[date_col], errors='coerce') 
            valid_dates = date_series.dropna() # Remove any rows where conversion failed (NaT).

            # Proceed only if there are valid dates after conversion and dropping NaNs.
            if not valid_dates.empty:
                min_data_date = valid_dates.min().date() # Get the earliest date from the valid data.
                max_data_date = valid_dates.max().date() # Get the latest date from the valid data.

                # --- Initialize Session State if Needed --- # Set default dates if not already in session state.
                # Initialize state only if keys are completely absent or have value None.
                if start_key not in st.session_state or st.session_state[start_key] is None:
                    st.session_state[start_key] = min_data_date # Default start date to the minimum found in data.
                if end_key not in st.session_state or st.session_state[end_key] is None:
                    st.session_state[end_key] = max_data_date   # Default end date to the maximum found in data.

                # --- Create Date Input Widgets --- # Use columns for layout.
                col1, col2 = st.sidebar.columns(2) # Place date inputs side-by-side.
                with col1:
                    st.date_input(
                        start_label, # Label for the start date widget.
                        min_value=min_data_date, # Set the minimum allowed date based on data.
                        max_value=max_data_date, # Set the maximum allowed date based on data.
                        key=start_key          # Link widget to session state for start date.
                    )
                with col2:
                    st.date_input(
                        end_label, # Label for the end date widget.
                        min_value=min_data_date, # Set the minimum allowed date based on data.
                        max_value=max_data_date, # Set the maximum allowed date based on data.
                        key=end_key            # Link widget to session state for end date.
                    )
            # If no valid dates were found after attempting conversion.
            else:
                st.caption(f"Ingen gyldige datoer funnet i '{date_col}'.") # Inform user about lack of valid dates.
        # If the date column itself is missing from the DataFrame.
        else:
            st.caption(f"Data for '{start_label}/{end_label}' (kolonne: {date_col}) mangler.") # Inform user about missing date column. 
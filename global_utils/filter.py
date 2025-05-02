## Imports ##
import streamlit as st
import pandas as pd # Import pandas for DataFrame check in apply_filters

## Filter Definitions ##
# Define codes/labels/mappings used in status filters
REDLIST_CODES = ['CR', 'EN', 'VU', 'NT', 'LC', 'DD', 'NE']
ALIEN_CODES = ['SE', 'HI', 'PH', 'LO']
SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL = {
    "Prioriterte Arter": "Prioriterte arter",
    "Andre Spes. Hensyn": "Andre spesielt hensynskrevende arter",
    "Ansvarsarter": "Ansvarsarter",
    "Spes. Økol. Former": "Spesielle okologiske former",
    "Truede Arter": "Trua arter",
    "Fredete Arter": "Fredete arter"
}

## Functions ##

# --- Function: display_filter_widgets ---
# Creates Streamlit widgets for filtering the data.
# Assumes 'data' is a pandas DataFrame containing filterable columns.
# Stores selected filter values in st.session_state.
def display_filter_widgets(data):

    st.sidebar.header("Filtreringsvalg")  # Add a header to the sidebar section

    # --- General Text Search --- # Text input for general search
    filter_key_text = 'filter_general_text' # Session state key
    st.sidebar.text_input(
        "Generelt Tekstsøk",
        key=filter_key_text, # Use the specific key
        placeholder="Søk i alle tekstfelt..." # Placeholder text
    )

    with st.sidebar.expander("Taksonomi", expanded=False):

        # --- Familie Filter ---
        original_col_name_familie = "FamilieNavn"
        filter_key_familie = 'filter_familie'
        display_label_familie = "Familie"
        if original_col_name_familie in data.columns:
            unique_values_familie = sorted(list(data[original_col_name_familie].dropna().unique())) # Get unique AND sort
            if unique_values_familie:
                st.multiselect(
                    display_label_familie,
                    options=unique_values_familie,
                    key=filter_key_familie
                )
            else:
                 st.caption(f"Ingen unike verdier for '{display_label_familie}'.") # Caption if column exists but no unique values
        else:
            st.caption(f"Data for '{display_label_familie}' mangler.")

        # --- Orden Filter ---
        original_col_name_orden = "OrdenNavn"
        filter_key_orden = 'filter_orden'
        display_label_orden = "Orden"
        if original_col_name_orden in data.columns:
            unique_values_orden = sorted(list(data[original_col_name_orden].dropna().unique())) # Get unique AND sort
            if unique_values_orden:
                st.multiselect(
                    display_label_orden,
                    options=unique_values_orden,
                    key=filter_key_orden
                )
            else:
                 st.caption(f"Ingen unike verdier for '{display_label_orden}'.")
        else:
            st.caption(f"Data for '{display_label_orden}' mangler.")

        # --- Art Filter (Species) ---
        original_col_name_art = "preferredPopularName"
        filter_key_art = 'filter_art'
        display_label_art = "Art"
        if original_col_name_art in data.columns:
            unique_values_art = sorted(list(data[original_col_name_art].dropna().unique())) # Get unique AND sort
            if unique_values_art:
                st.multiselect(
                    display_label_art,
                    options=unique_values_art,
                    key=filter_key_art
                )
            else:
                 st.caption(f"Ingen unike verdier for '{display_label_art}'.")
        else:
            st.caption(f"Data for '{display_label_art}' mangler.")

    # --- Status Expander --- # Expander for status filters
    with st.sidebar.expander("Status", expanded=False):
        category_col = "category" # Original column name for Red List / Alien status

        # --- Red List Filter ---
        filter_key_redlist = 'filter_redlist_category'
        display_label_redlist = "Rødlistekategori"
        if category_col in data.columns:
            # Get unique non-null values from the category column first
            unique_data_categories = data[category_col].dropna().unique()
            # Filter these unique values against our predefined REDLIST_CODES
            options_redlist = sorted([code for code in unique_data_categories if code in REDLIST_CODES])
            if options_redlist: # Only display if there are valid options
                st.multiselect(
                    display_label_redlist,
                    options=options_redlist,
                    key=filter_key_redlist
                )
            else:
                st.caption(f"Ingen relevante '{display_label_redlist}' funnet.") # Caption if no relevant codes found
        else:
            st.caption(f"Data for '{display_label_redlist}' (kolonne: {category_col}) mangler.")

        # --- Special Category Filter ---
        filter_key_special = 'filter_special_category'
        display_label_special = "Arter av nasjonal forvaltningsstatus"
        options_special = [] # Initialize empty list for options
        # Check which special status columns exist AND have at least one 'Yes'
        for label, original_col in SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL.items():
            if original_col in data.columns and (data[original_col] == 'Yes').any():
                options_special.append(label) # Add the label if relevant data exists

        if options_special: # Only display if there are valid options
            st.multiselect(
                display_label_special,
                options=sorted(options_special), # Sort the discovered options
                key=filter_key_special
            )
        else:
            st.caption(f"Ingen relevante '{display_label_special}' funnet.") # Caption if no relevant statuses found

        # --- Alien Species Filter ---
        filter_key_alien = 'filter_alien_category'
        display_label_alien = "Fremmedartrisiko"
        if category_col in data.columns:
            # Get unique non-null values from the category column first
            unique_data_categories = data[category_col].dropna().unique()
            # Filter these unique values against our predefined ALIEN_CODES
            options_alien = sorted([code for code in unique_data_categories if code in ALIEN_CODES])
            if options_alien: # Only display if there are valid options
                st.multiselect(
                    display_label_alien,
                    options=options_alien,
                    key=filter_key_alien
                )
            else:
                st.caption(f"Ingen relevante '{display_label_alien}' funnet.") # Caption if no relevant codes found
        else:
            st.caption(f"Data for '{display_label_alien}' (kolonne: {category_col}) mangler.")

    # --- Date Range Expander --- # Expander for date range filter
    with st.sidebar.expander("Tidsperiode", expanded=False):
        date_col = "dateTimeCollected" # Original column name for date/time
        start_key = 'filter_start_date' # Session state key for start date
        end_key = 'filter_end_date'   # Session state key for end date
        start_label = "Startdato"    # Display label for start date
        end_label = "Sluttdato"      # Display label for end date

        # Check if date column exists
        if date_col in data.columns:
            # Attempt to convert to datetime, coerce errors to NaT
            date_series = pd.to_datetime(data[date_col], errors='coerce')
            valid_dates = date_series.dropna() # Drop NaT values

            # Proceed only if there are valid dates
            if not valid_dates.empty:
                min_data_date = valid_dates.min().date() # Get the minimum date from data
                max_data_date = valid_dates.max().date() # Get the maximum date from data

                # --- Initialize Session State if Needed ---
                # Initialize state only if keys are completely absent or None
                if start_key not in st.session_state or st.session_state[start_key] is None:
                    st.session_state[start_key] = min_data_date # Default start to min date
                if end_key not in st.session_state or st.session_state[end_key] is None:
                    st.session_state[end_key] = max_data_date   # Default end to max date

                # --- Create Widgets (Read from Session State via Key) ---
                col1, col2 = st.sidebar.columns(2) # Use sidebar columns for better layout
                with col1:
                    st.date_input(
                        start_label,
                        min_value=min_data_date, # Overall min from data
                        max_value=max_data_date, # Overall max from data
                        key=start_key          # Link to start date state
                    )
                with col2:
                    st.date_input(
                        end_label,
                        min_value=min_data_date, # Overall min from data
                        max_value=max_data_date, # Overall max from data
                        key=end_key            # Link to end date state
                    )
            else:
                st.caption(f"Ingen gyldige datoer funnet i '{date_col}'.") # Show caption if no valid dates.
        else:
            st.caption(f"Data for '{start_label}/{end_label}' (kolonne: {date_col}) mangler.") # Show caption if no data.

# --- Function: apply_filters ---
# Filters the DataFrame based on values stored in st.session_state.
# Assumes 'data' is a pandas DataFrame and session state keys match widgets.
def apply_filters(data):
    """Applies filters selected via widgets to the DataFrame.

    Reads filter values from st.session_state and returns a filtered DataFrame.
    Returns the original DataFrame if no filters are active or data is empty.
    """
    if data.empty:
        return data  # Return empty if input is empty

    filtered_data = data.copy()  # Start with a copy of the original data

    # --- Apply Specific Column Filters FIRST --- # Apply expander filters

    # --- Apply Taxonomic Filters --- # Section for taxonomic filters

    # --- Apply 'Familie' Filter (using original column name) ---
    original_col_name = "FamilieNavn"  # Define the original column name for Familie
    filter_key = 'filter_familie'  # Define the session state key for Familie filter

    # Check if the filter key exists in session state
    if filter_key in st.session_state:
        selected_values = st.session_state[filter_key]  # Retrieve selected families

        # --- Apply filter ONLY if selections were made --- # Check if the list of selected values is not empty
        if selected_values:  # Only proceed if the user selected at least one family
            # Apply the filter if the original column exists in the DataFrame
            if original_col_name in filtered_data.columns:
                # Filter the DataFrame based on the selected families using the original column name.
                filtered_data = filtered_data[filtered_data[original_col_name].isin(selected_values)]

    # --- Apply 'Orden' Filter (using original column name) ---
    original_col_name_orden = "OrdenNavn" # Define the original column name for Orden
    filter_key_orden = 'filter_orden' # Define the session state key for Orden filter

    # Check if the filter key exists in session state
    if filter_key_orden in st.session_state:
        selected_ordener = st.session_state[filter_key_orden] # Retrieve selected ordener

        # --- Apply filter ONLY if selections were made --- # Check if the list of selected values is not empty
        if selected_ordener: # Only proceed if the user selected at least one orden
            # Apply the filter if the original column exists in the DataFrame
            if original_col_name_orden in filtered_data.columns:
                # Filter the DataFrame based on the selected ordener using the original column name.
                filtered_data = filtered_data[filtered_data[original_col_name_orden].isin(selected_ordener)]

    # --- Apply 'Art' Filter (using original column name) ---
    original_col_name_art = "preferredPopularName" # Define the original column name for Art
    filter_key_art = 'filter_art' # Define the session state key for Art filter

    # Check if the filter key exists in session state
    if filter_key_art in st.session_state:
        selected_arter = st.session_state[filter_key_art] # Retrieve selected arter

        # --- Apply filter ONLY if selections were made --- # Check if the list of selected values is not empty
        if selected_arter: # Only proceed if the user selected at least one art
            # Apply the filter if the original column exists in the DataFrame
            if original_col_name_art in filtered_data.columns:
                # Filter the DataFrame based on the selected arter using the original column name.
                filtered_data = filtered_data[filtered_data[original_col_name_art].isin(selected_arter)]

    # --- Apply Status Filters --- # Section for status filters
    category_col = "category" # Original column for Red List / Alien status

    # --- Apply Red List Filter ---
    filter_key_redlist = 'filter_redlist_category'
    if filter_key_redlist in st.session_state and st.session_state[filter_key_redlist]:
        selected_values = st.session_state[filter_key_redlist]
        if category_col in filtered_data.columns:
            filtered_data = filtered_data[filtered_data[category_col].isin(selected_values)]

    # --- Apply Special Category Filter ---
    filter_key_special = 'filter_special_category'
    if filter_key_special in st.session_state and st.session_state[filter_key_special]:
        selected_labels = st.session_state[filter_key_special]
        # Combine conditions: row must have 'Yes' in AT LEAST ONE selected special status column
        combined_condition = pd.Series(False, index=filtered_data.index) # Start with all False
        for label in selected_labels:
            original_col_special = SPECIAL_STATUS_LABEL_TO_ORIGINAL_COL.get(label)
            if original_col_special and original_col_special in filtered_data.columns:
                # Update condition where this column is 'Yes' (use | for OR)
                combined_condition = combined_condition | (filtered_data[original_col_special] == 'Yes')
        filtered_data = filtered_data[combined_condition] # Apply combined condition

    # --- Apply Alien Species Filter ---
    filter_key_alien = 'filter_alien_category'
    if filter_key_alien in st.session_state and st.session_state[filter_key_alien]:
        selected_values = st.session_state[filter_key_alien]
        if category_col in filtered_data.columns:
            filtered_data = filtered_data[filtered_data[category_col].isin(selected_values)]

    # --- Apply Date Range Filter --- # Section for date range filter
    date_col = "dateTimeCollected" # Original column name
    start_key = 'filter_start_date' # Session state key for start date
    end_key = 'filter_end_date'   # Session state key for end date

    # Get start and end dates from session state
    start_date = st.session_state.get(start_key)
    end_date = st.session_state.get(end_key)

    # Proceed only if both dates are available (not None) and the column exists
    if start_date is not None and end_date is not None and date_col in filtered_data.columns:

        # Ensure start_date is not after end_date (basic validation)
        if start_date <= end_date:
            # Convert the column to datetime objects, coercing errors
            date_col_dt = pd.to_datetime(filtered_data[date_col], errors='coerce')

            # Create a boolean mask for valid dates within the range
            date_mask = (
                date_col_dt.notna() &
                (date_col_dt.dt.date >= start_date) &
                (date_col_dt.dt.date <= end_date)
            )
            # Apply the mask
            filtered_data = filtered_data[date_mask]
        # else: # Optional: Add a warning if start date is after end date
            # st.sidebar.warning("Startdato kan ikke være etter sluttdato.")

    # --- Apply General Text Search LAST --- # Apply the text search filter
    filter_key_text = 'filter_general_text' # Session state key
    search_text = st.session_state.get(filter_key_text, "").strip() # Get search text, default empty

    if search_text: # Proceed only if search text is provided
        # Select columns with string-like data (object dtype)
        string_columns = filtered_data.select_dtypes(include='object').columns

        if not string_columns.empty:
            # Split search text into terms (words)
            search_terms = search_text.split()

            # Initialize final mask to include all rows initially
            final_mask = pd.Series(True, index=filtered_data.index)

            # Apply each search term using AND logic
            for term in search_terms:
                # Mask for current term: True if term found in ANY string column for the row
                term_mask = filtered_data[string_columns].apply(
                    lambda row: row.astype(str).str.contains(term, case=False, na=False).any(),
                    axis=1
                )
                # Combine with final mask using AND
                final_mask = final_mask & term_mask

            # Apply the final combined mask
            filtered_data = filtered_data[final_mask]

    return filtered_data  # Return the filtered DataFrame

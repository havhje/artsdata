## Imports ##
import streamlit as st


## Functions ##

# --- Function: display_filter_widgets ---
# Creates Streamlit widgets for filtering the data.
# Assumes 'data' is a pandas DataFrame containing filterable columns.
# Stores selected filter values in st.session_state.
def display_filter_widgets(data):
    """Displays filter widgets in the Streamlit sidebar.

    Uses the provided DataFrame to populate filter options and stores
    user selections in st.session_state.
    """
    st.sidebar.header("Filtreringsvalg")  # Add a header to the sidebar section

    # --- Filter by 'Familie' (using original column name) ---
    original_col_name = "FamilieNavn"  # Define the original column name for Familie
    filter_key = 'filter_familie'  # Define the session state key for Familie filter
    display_label = "Velg Familie(r)"  # Define the display label for the user

    # Check if data is not empty and the original column exists before creating widget
    if not data.empty and original_col_name in data.columns:
        # Get unique, non-null values for the filter options from the original column
        unique_values = data[original_col_name].dropna().unique()
        # Create multiselect widget. Default to an empty list (no selection).
        st.sidebar.multiselect(
            display_label,
            options=unique_values,
            default=[],  # Set default to empty list - nothing selected initially
            key=filter_key  # Use the specific key for Familie filter
        )
    else:
        # Placeholder if no data/column
        st.sidebar.text(f"Ingen data for {original_col_name}.")  # Update message

    # --- Add more filter widgets here ---
    # Example: Filter by 'Orden' (Commented out)
    # original_col_name_orden = "OrdenNavn"
    # filter_key_orden = 'filter_orden'
    # display_label_orden = "Velg Orden(er)"
    # if not data.empty and original_col_name_orden in data.columns:
    #     unique_ordener = data[original_col_name_orden].dropna().unique()
    #     st.sidebar.multiselect(
    #         display_label_orden,
    #         options=unique_ordener,
    #         default=[],
    #         key=filter_key_orden
    #     )
    # else:
    #     st.sidebar.text(f"Ingen data for {original_col_name_orden}.")

    st.sidebar.info("Flere filtre kommer...")  # Placeholder message


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

    # --- Apply other filters here ---
    # Example: Apply 'Orden' filter (Commented out)
    # original_col_name_orden = "OrdenNavn"
    # filter_key_orden = 'filter_orden'
    # if filter_key_orden in st.session_state:
    #     selected_ordener = st.session_state[filter_key_orden]
    #     if selected_ordener:
    #         if original_col_name_orden in filtered_data.columns:
    #             filtered_data = filtered_data[filtered_data[original_col_name_orden].isin(selected_ordener)]

    return filtered_data  # Return the filtered DataFrame

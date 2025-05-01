## Imports ##
import streamlit as st


## Functions ##

# --- Function: display_filter_widgets ---
# Creates Streamlit widgets for filtering the data.
# Assumes 'data' is a pandas DataFrame containing filterable columns.
# Stores selected filter values in st.session_state.
def display_filter_widgets(data):

    st.sidebar.header("Filtreringsvalg")  # Add a header to the sidebar section

    with st.sidebar.expander("Taksonomi", expanded=False):

        # --- Familie Filter ---
        original_col_name_familie = "FamilieNavn"  # Define the original column name for Familie
        filter_key_familie = 'filter_familie'  # Define the session state key for Familie filter
        display_label_familie = "Familie"  # Define the display label for the user
        unique_values_familie = data[original_col_name_familie].dropna().unique() # Get unique, non-null values for the filter options from the original column

        st.multiselect(
            display_label_familie,
            options=unique_values_familie,
            default=[],  # Set default to empty list - nothing selected initially
            key=filter_key_familie  # Use the specific key for Familie filter
            )

        # --- Orden Filter ---
        original_col_name_orden = "OrdenNavn"  # Define the original column name for Orden
        filter_key_orden = 'filter_orden' # Define the session state key for Orden filter
        display_label_orden = "Orden"  # Define the display label for the user
        unique_values_orden = data[original_col_name_orden].dropna().unique() # Get unique, non-null values for the filter options

        st.multiselect(
            display_label_orden,
            options=unique_values_orden,
            default=[], # Set default to empty list
            key=filter_key_orden # Use the specific key for Orden filter
            )

        # --- Art Filter (Species) ---
        original_col_name_art = "preferredPopularName" # Define the original column name for Art (Species)
        filter_key_art = 'filter_art' # Define the session state key for Art filter
        display_label_art = "Art" # Define the display label for the user
        unique_values_art = data[original_col_name_art].dropna().unique() # Get unique, non-null values for the filter options

        st.multiselect( # Use st.multiselect directly inside the sidebar expander
            display_label_art,
            options=unique_values_art,
            default=[], # Set default to empty list
            key=filter_key_art # Use the specific key for Art filter
            )





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

    # --- Apply other filters here ---
    # Example: Apply 'Genus' filter (template)
    # original_col_name_genus = "GenusNavn"

    return filtered_data  # Return the filtered DataFrame

## Imports ##
import streamlit as st
import pandas as pd

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

    # --- Example: Filter by 'Taksonomisk Gruppe' ---
    # Check if data is not empty and column exists before creating widget
    if not data.empty and "Taksonomisk Gruppe" in data.columns:
        # Get unique, non-null values for the filter options
        unique_groups = data["Taksonomisk Gruppe"].dropna().unique()
        # Create multiselect widget. Default to all selected if state not set.
        # Key is used to store/retrieve value from session_state
        # The return value is assigned but not used here; we rely on session state.
        st.sidebar.multiselect(
            "Velg Taksonomisk Gruppe(r)",
            options=unique_groups,
            default=list(unique_groups),
            key='filter_taksonomisk_gruppe'  # Store selection in session state
        )
    else:
        # Placeholder if no data/column
        st.sidebar.text("Ingen data for Taksonomisk Gruppe.")

    # --- Add more filter widgets here ---
    # Example: Filter by 'Orden'
    # if not data.empty and "Orden" in data.columns:
    #     unique_ordener = data["Orden"].dropna().unique()
    #     st.sidebar.multiselect(
    #         "Velg Orden(er)",
    #         options=unique_ordener,
    #         default=list(unique_ordener),
    #         key='filter_orden'
    #     )

    # Example: Date range slider (requires a date column)
    # if not data.empty and 'Dato' in data.columns:
    #     # Ensure 'Dato' is datetime type (add error handling)
    #     # data['Dato'] = pd.to_datetime(data['Dato'])
    #     min_date = data['Dato'].min()
    #     max_date = data['Dato'].max()
    #     st.sidebar.date_input(
    #         "Velg Datoområde",
    #         value=(min_date, max_date),
    #         min_value=min_date,
    #         max_value=max_date,
    #         key='filter_date_range'
    #      )

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

    # --- Apply 'Taksonomisk Gruppe' Filter ---
    # Check if the filter key exists in session state
    if 'filter_taksonomisk_gruppe' in st.session_state:
        selected_groups = st.session_state['filter_taksonomisk_gruppe']
        # Apply the filter if the column exists in the DataFrame
        if "Taksonomisk Gruppe" in filtered_data.columns:
            # Filter the DataFrame based on the selected groups
            filtered_data = filtered_data[
                filtered_data["Taksonomisk Gruppe"].isin(selected_groups)
            ]

    # --- Apply other filters here ---
    # Example: Apply 'Orden' filter
    # if 'filter_orden' in st.session_state:
    #     selected_ordener = st.session_state['filter_orden']
    #     if "Orden" in filtered_data.columns:
    #         filtered_data = filtered_data[filtered_data["Orden"].isin(selected_ordener)]

    # Example: Apply Date range filter
    # if 'filter_date_range' in st.session_state:
    #     start_date, end_date = st.session_state['filter_date_range']
    #     if 'Dato' in filtered_data.columns:
    #         # Ensure 'Dato' is datetime for comparison
    #         # filtered_data['Dato'] = pd.to_datetime(filtered_data['Dato'])
    #         # Compare dates properly
    #         start_date_dt = pd.to_datetime(start_date)
    #         end_date_dt = pd.to_datetime(end_date)
    #         filtered_data = filtered_data[
    #             (filtered_data['Dato'] >= start_date_dt) & (filtered_data['Dato'] <= end_date_dt)
    #         ]

    return filtered_data  # Return the filtered DataFrame

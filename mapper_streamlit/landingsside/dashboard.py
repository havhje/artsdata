# ##### Imports #####
import streamlit as st # Import Streamlit for app structure and widgets.
# pandas import removed as it's unused here now.

# --- Import Local Utilities ---
# Formatting Helpers
from .utils_dashboard.formatering_md_tekst import (
    format_top_observations_md,
    format_top_agg_md,
    format_top_frequency_md
)
# Calculation Functions
from .utils_dashboard.calculations.calculate_basic_metrics import calculate_basic_metrics
from .utils_dashboard.calculations.calculate_redlists_alien_forvaltning_stats import calculate_all_status_counts
from .utils_dashboard.calculations.calculate_top_lists import calculate_all_top_lists
# Display Functions
# display_date_range removed from this import
from .utils_dashboard.display_UI.display_kartleggings_info import display_main_metrics_grid
from .utils_dashboard.display_UI.display_rødliste_fremmedarter_arter_av_forvaltningsinteresse import display_all_status_sections
# Figure Functions (New)
from .figures_dashboard.obs_periode_calculations import calculate_yearly_metrics # Import yearly metrics calculation.
from .figures_dashboard.obs_periode_figur import create_observation_period_figure # Import figure creation.


##### Main Dashboard Function #####

# --- Function: display_dashboard ---
# Orchestrates the calculation and display of the main dashboard components.
# Takes a pandas DataFrame 'data' containing the observation records (with renamed columns).
def display_dashboard(data):
    # --- Initialize Session State for Top 10 Visibility ---
    # Ensures state persists across reruns for toggling lists via button.
    if 'show_dashboard_top_lists' not in st.session_state:
        st.session_state.show_dashboard_top_lists = False # Default: hide all top lists on first run.

    # --- Empty Data Check ---
    if data.empty:  # Checks if the input DataFrame is empty.
        st.warning("Ingen data matcher de valgte filtrene.")  # Display warning if no data.
        return  # Stop execution for this dashboard if no data.

    # --- Perform All Calculations ---
    # Calculate basic metrics (totals, uniques, dates)
    basic_metrics = calculate_basic_metrics(data) # Returns a dictionary.
    # Calculate status counts (red list, alien, special)
    status_counts = calculate_all_status_counts(data) # Returns a dictionary.
    # Calculate all top lists (frequency, individuals, aggregated)
    top_lists = calculate_all_top_lists(data, top_n=10) # Returns a dictionary of DataFrames/dicts.

    # Calculate yearly metrics for the figure (New - passing column names)
    # Define the renamed columns expected by the calculation function.
    date_col_renamed = "Innsamlingsdato/-tid"
    individuals_col_renamed = "Antall Individer"
    # Call the calculation function with the data and specific column names.
    yearly_metrics_data = calculate_yearly_metrics(
        data, # The DataFrame (should have renamed columns).
        date_col_name=date_col_renamed, # Pass the expected date column name.
        individuals_col_name=individuals_col_renamed # Pass the expected individuals column name.
    )

    # Package formatting functions for easy passing
    formatting_funcs = {
        "format_top_observations_md": format_top_observations_md,
        "format_top_agg_md": format_top_agg_md,
        "format_top_frequency_md": format_top_frequency_md
    }

    # --- Display Section ---
    # Header and main toggle button side-by-side
    header_cols = st.columns([0.8, 0.2]) # Allocate space: 80% for header, 20% for button.
    with header_cols[0]:
        st.markdown("##### Kartleggingsstatestikk")
    with header_cols[1]:
        # Button to toggle visibility of all Top 10 lists in this dashboard section.
        if st.button("Topp 10", key="toggle_all_dashboard_lists"): # Use a specific key for this button.
             st.session_state.show_dashboard_top_lists = not st.session_state.show_dashboard_top_lists # Toggle the boolean state.

    # --- Display Main Metrics Grid ---
    # Calls the function to render the top 5-column grid with metrics and conditional lists.
    display_main_metrics_grid(
        metrics=basic_metrics,
        top_lists=top_lists,
        show_top_lists=st.session_state.show_dashboard_top_lists,
        formatters=formatting_funcs
    )

    # --- Display Status Sections ---
    # Calls the function to render Red List, Alien, and Special Status sections.
    display_all_status_sections(
        status_counts=status_counts,
        top_lists=top_lists,
        show_top_lists=st.session_state.show_dashboard_top_lists,
        formatters=formatting_funcs
    )

    # --- Display Observation Period Figure (New Interactive Version) ---
    st.markdown("--- ") # Add a separator before the figure section.
    st.markdown("##### Observasjoner over tid") # Add a subheader for the figure.

    # Check if data for the figure exists
    if not yearly_metrics_data.empty:
        # Define the available traces for selection
        available_traces = [
            'Antall Observasjoner',
            'Antall Individer',
            'Gj.snitt Individer/Observasjon'
        ]
        # Create the multiselect widget
        selected_traces = st.multiselect(
            label="Velg metrikker å vise i figuren:", # Widget label.
            options=available_traces, # Options are the trace names.
            default=available_traces[0:2] # Default to showing the first two (Obs & Individer).
        )

        # Only create and display the figure if at least one trace is selected
        if selected_traces:
            # Create the figure using the calculated yearly data and selected traces.
            observation_period_fig = create_observation_period_figure(
                yearly_data=yearly_metrics_data,
                traces_to_show=selected_traces # Pass the user's selection.
                )
            # Display the Plotly figure using Streamlit.
            st.plotly_chart(observation_period_fig, use_container_width=True) # Display the chart, making it fit the container width.
        else:
            # Message if the user deselects all options.
            st.info("Velg minst én metrikk for å vise figuren.") # Prompt user to select traces.

    else:
        # Optional: Display a message if no data is available for the chart initially
        st.info("Ingen data tilgjengelig for observasjonsperiodefiguren etter filtrering eller databehandling.") # Inform user about missing chart data.

    # --- Removed Observation Period Text Display ---
    # display_date_range(metrics=basic_metrics) # This line is removed.

    # Add a final separator for visual spacing
    st.markdown("---")

# ##### Main Execution Block (Optional) #####
# if __name__ == '__main__':
    # Example Usage (Requires sample data loading)
    # sample_df = pd.DataFrame(...) # Load or create sample data
    # display_dashboard(sample_df)
#     pass # Keep minimal as per rules, no print statements here.

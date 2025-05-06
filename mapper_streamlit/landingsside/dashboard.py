# ##### Imports #####
import streamlit as st # Import Streamlit for app structure and widgets.
import pandas as pd # Import pandas for DataFrame manipulation (used for renaming top_lists).
import io # For st.write(df.info())

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
from .utils_dashboard.display_UI.display_kartleggings_info import display_main_metrics_grid
from .utils_dashboard.display_UI.display_rødliste_fremmedarter_arter_av_forvaltningsinteresse import display_all_status_sections
# Figure Functions
from .figures_dashboard.obs_periode_calculations import calculate_yearly_metrics # Import yearly metrics calculation.
from .figures_dashboard.obs_periode_figur import create_observation_period_figure # Import figure creation.
# Import for renaming
from global_utils.column_mapping import get_display_name # For renaming columns to display names.


##### Main Dashboard Function #####

# --- Function: display_dashboard ---
# Orchestrates the calculation and display of the main dashboard components.
# Takes a pandas DataFrame 'data' containing observation records with ORIGINAL column names.
def display_dashboard(data, 
                        # Define actual original column names your data uses.
                        # These are placeholders, replace with your actual original column names.
                        original_art_col: str = "Art", # Placeholder: e.g., "scientificName"
                        original_family_col: str = "Familie", # Placeholder: e.g., "family"
                        original_observer_col: str = "Innsamler/Observatør", # Placeholder: e.g., "recordedBy"
                        original_individual_count_col: str = "Antall Individer", # Placeholder: e.g., "individualCount"
                        original_event_date_col: str = "Innsamlingsdato/-tid", # Placeholder: e.g., "eventDate"
                        original_category_col: str = "Kategori (Rødliste/Fremmedart)", # Placeholder: e.g., "category"
                        original_alien_flag_col: str = "Fremmede arter kategori", # Placeholder: e.g., "Fremmede arter"
                        original_special_status_cols_list: list = [ # Placeholder list of original names
                            "Prioriterte Arter", "Andre Spes. Hensyn.", "Ansvarsarter", "Spes. Økol. Former"
                            ]
                        ):
    # --- Initialize Session State for Top 10 Visibility --- 
    if 'show_dashboard_top_lists' not in st.session_state:
        st.session_state.show_dashboard_top_lists = False

    if data.empty:  
        st.warning("Ingen data matcher de valgte filtrene.")
        return

    # --- Perform All Calculations (using original column names) ---
    basic_metrics = calculate_basic_metrics(
        data,
        individual_count_col=original_individual_count_col,
        art_col=original_art_col,
        family_col=original_family_col,
        observer_col=original_observer_col,
        event_date_col=original_event_date_col
    )
    status_counts = calculate_all_status_counts(
        data,
        category_col=original_category_col,
        alien_flag_col=original_alien_flag_col,
        original_special_status_cols=original_special_status_cols_list
    )
    # Calculate all top lists. These will have original column names in the resulting DFs.
    raw_top_lists = calculate_all_top_lists(
        data, top_n=10,
        art_col=original_art_col,
        family_col=original_family_col,
        observer_col=original_observer_col,
        individual_count_col=original_individual_count_col,
        category_col=original_category_col,
        original_special_status_cols=original_special_status_cols_list
    )

    yearly_metrics_data = calculate_yearly_metrics(
        data, 
        date_col_name=original_event_date_col, 
        individuals_col_name=original_individual_count_col
    )

    # --- Prepare Top Lists for Display (Rename Columns) ---
    # The formatting functions expect display names, so we rename columns here.
    display_top_lists = {}
    for key, df_or_dict in raw_top_lists.items():
        if isinstance(df_or_dict, pd.DataFrame):
            df_renamed = df_or_dict.copy()
            # Robustly get display names, fallback to original if no mapping (inherent in .get())
            df_renamed.columns = [get_display_name(col) for col in df_renamed.columns]
            display_top_lists[key] = df_renamed
        elif isinstance(df_or_dict, dict): # For nested dicts of DataFrames
            renamed_inner_dict = {}
            for inner_key, df_inner in df_or_dict.items():
                if isinstance(df_inner, pd.DataFrame):
                    df_inner_renamed = df_inner.copy()
                    df_inner_renamed.columns = [get_display_name(col) for col in df_inner_renamed.columns]
                    renamed_inner_dict[inner_key] = df_inner_renamed
                else:
                    renamed_inner_dict[inner_key] = df_inner 
            display_top_lists[key] = renamed_inner_dict
        else:
            display_top_lists[key] = df_or_dict 

    formatting_funcs = {
        "format_top_observations_md": format_top_observations_md,
        "format_top_agg_md": format_top_agg_md,
        "format_top_frequency_md": format_top_frequency_md
    }

    # --- Display Section --- 
    header_cols = st.columns([0.8, 0.2])
    with header_cols[0]:
        st.markdown("##### Kartleggingsstatestikk")
    with header_cols[1]:
        if st.button("Topp 10", key="toggle_all_dashboard_lists"): 
             st.session_state.show_dashboard_top_lists = not st.session_state.show_dashboard_top_lists

    display_main_metrics_grid(
        metrics=basic_metrics,
        top_lists=display_top_lists, # Pass renamed top_lists
        show_top_lists=st.session_state.show_dashboard_top_lists,
        formatters=formatting_funcs
    )

    display_all_status_sections(
        status_counts=status_counts,
        top_lists=display_top_lists, # Pass renamed top_lists
        show_top_lists=st.session_state.show_dashboard_top_lists,
        formatters=formatting_funcs
    )

    st.markdown("--- ") 
    st.markdown("##### Observasjoner over tid") 

    if not yearly_metrics_data.empty:
        # These trace names are display names and should match columns from calculate_yearly_metrics output.
        available_traces = [
            'Antall Observasjoner', 
            'Antall Individer', 
            'Gj.snitt Individer/Observasjon'
        ]
        # Ensure that yearly_metrics_data columns match these trace names or map them.
        # Assuming calculate_yearly_metrics returns: 'Year', 'Sum_Observations', 'Sum_Individuals', 'Avg_Individuals_Per_Observation'
        # We map display trace names to these output columns:
        trace_to_col_map = {
            'Antall Observasjoner': 'Sum_Observations',
            'Antall Individer': 'Sum_Individuals',
            'Gj.snitt Individer/Observasjon': 'Avg_Individuals_Per_Observation'
        }
        # Filter available_traces based on what columns actually exist in yearly_metrics_data for robustness
        actual_available_traces = [trace for trace, col_name in trace_to_col_map.items() if col_name in yearly_metrics_data.columns]

        selected_traces_display = st.multiselect(
            label="Velg metrikker å vise i figuren:", 
            options=actual_available_traces, 
            default=[t for t in actual_available_traces if t in ['Antall Observasjoner', 'Antall Individer']] 
        )

        if selected_traces_display:
            # Map selected display names back to the actual column names for the figure creation function
            selected_cols_for_figure = [trace_to_col_map[trace] for trace in selected_traces_display]
            observation_period_fig = create_observation_period_figure(
                yearly_data=yearly_metrics_data,
                traces_to_show=selected_cols_for_figure 
                )
            st.plotly_chart(observation_period_fig, use_container_width=True) 
        else:
            st.info("Velg minst én metrikk for å vise figuren.")
    else:
        st.info("Ingen data tilgjengelig for observasjonsperiodefiguren.")

    st.markdown("--- ")

# if __name__ == '__main__':
#     pass 

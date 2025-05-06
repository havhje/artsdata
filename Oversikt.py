# Oversikt.py
##### Imports #####
import streamlit as st # Used for Streamlit app elements, page configuration, and session state.
import pandas as pd # Used for DataFrame operations and type hints (though type hints are omitted for now).
from pathlib import Path # Used for constructing file paths.
from global_utils.column_mapping import get_display_name # Used for mapping original column names to display names.
from mapper_streamlit.landingsside.dashboard import display_dashboard # Used to display the dashboard component.
from global_utils.filtering.filter_ui import display_filter_widgets # Used to display filter UI components.
from global_utils.filtering.filter_logic import apply_filters # Used to apply filter logic to data.
from global_utils.session_state_manager import initialize_and_persist_filters # Used to manage filter state persistence.
from global_utils.data_loading import load_and_prepare_data # Imports the new centralized data loading function.
from global_utils.filtering.filter_constants import ALIEN_CODES # Imports constants for alien species filtering.

##### Initialize/Persist Session State #####
initialize_and_persist_filters() # Ensures filter state persists across pages. Must be called early.

##### Page Configuration #####
st.set_page_config(layout="wide") # Sets the page layout to wide mode.

##### Static Page Content #####
st.title("Velkommen til artsanalyse") # Sets the main title of the page.
st.write("Laget av Håvard Hjermstad-Sollerud") # Adds an authorship note.
st.subheader("Hva er dette?") # Adds a subheader for introductory text.
st.write(
    """Dette er en webapplikasjon som gjør at du kan se på data """ # Introductory paragraph.
    """fra Artsdatabanken."""
)

##### File Input Logic #####
# --- Determine File Input Source ---
taxonomy_file_default_path = Path(__file__).parent / "databehandling/output/Andøya_fugl_taxonomy.csv" # Defines the path to a local default CSV file.
file_input_for_loader = taxonomy_file_default_path # Initially assumes the local default file will be used.

# --- File Uploader --- # Moved from sidebar to main page
with st.expander("Last opp datafil"):
    uploaded_file = st.file_uploader(
        "Velg CSV-fil (Erstatter lokal fil hvis valgt)", # Label for the file uploader widget.
        type="csv" # Restricts file types to CSV.
    )

if uploaded_file is not None: # Checks if a file has been uploaded by the user.
    file_input_for_loader = uploaded_file # If uploaded, it overrides the default local file path.
# No explicit 'else' here for the happy path; if no upload, default path remains.

##### Data Loading #####
# --- Load and Prepare Data using Centralized Function ---
# This call uses the cached function from data_loader.py.
innlastet_data = load_and_prepare_data(file_input_for_loader) # Loads and preprocesses data. Assumes file_input_for_loader is valid.

##### Main Application Logic (Conditional on Data Loaded) #####
# --- Store Loaded Data in Session State (Simplified) ---
# This ensures 'loaded_data' in session_state reflects the current data.
st.session_state['loaded_data'] = innlastet_data # Updates session state with the loaded data.

# --- Display Filter Widgets in Sidebar ---
# st.sidebar.divider() # Visual separator.
# st.sidebar.header("Filtreringsvalg") # Header for filter section.
display_filter_widgets(innlastet_data) # Displays filter widgets. Assumes innlastet_data is a valid DataFrame for populating options.

# --- Apply Filters to Data ---
data_for_visning = apply_filters(innlastet_data) # Applies selected filters. Assumes filters are correctly applied to innlastet_data.

# --- Prepare Data for Dashboard ---
data_for_dashboard = data_for_visning.copy() # Creates a copy for dashboard-specific modifications.
data_for_dashboard.columns = [get_display_name(col) for col in data_for_dashboard.columns] # Renames columns for display.
st.subheader("Nøkkeltall") # Subheader for the dashboard section.
display_dashboard(data_for_dashboard) # Displays the dashboard. Assumes data_for_dashboard is correctly formatted.

# --- Define Alien Species Criteria ---
alien_col = "Fremmede arter" # Original column name for the dedicated alien flag.
category_col = "category" # Original column name for Red List / Alien Risk category.
alien_identifier = "Yes" # Value indicating alien species in alien_col.
category_identifiers = ALIEN_CODES # Values in category_col indicating alien species risk, from constants.

# --- Separate Alien and Non-Alien Species ---
# Initialize empty DataFrames with original columns for structure.
fremmede_arter_filtrert = pd.DataFrame(columns=data_for_visning.columns) # For alien species.
ikke_fremmede_arter_filtrert = data_for_visning.copy() # Default to all data as non-alien, will be overwritten if alien species are found.

# --- Build Alien Species Condition (Happy Path: assumes columns exist) ---
condition_alien_col_is_yes = (data_for_visning[alien_col].str.upper() == alien_identifier.upper()) # Condition for dedicated alien column. Assumes string comparison.
condition_category_is_alien = data_for_visning[category_col].isin(category_identifiers) # Condition for category column. Assumes .isin() works.
combined_alien_condition = condition_alien_col_is_yes | condition_category_is_alien # Combines conditions with OR.

fremmede_arter_filtrert = data_for_visning[combined_alien_condition] # Applies combined condition to get alien species.
ikke_fremmede_arter_filtrert = data_for_visning[~combined_alien_condition] # Applies inverse condition for non-alien species.


# --- Display Section: Main Table (Non-Alien Species) ---
st.subheader("Hovedoversikt (Ikke-fremmede arter)") # Subheader for the main table.
hovedtabell_visning = ikke_fremmede_arter_filtrert.copy() # Creates a copy for display modifications.
hovedtabell_visning.columns = [get_display_name(col) for col in hovedtabell_visning.columns] # Renames columns.

preferred_display_order = [ # Defines the preferred order of columns for display.
    "Taksonomisk Gruppe", "Orden", "Familie", "Art", "Antall Individer",
    "Kategori (Rødliste/Fremmedart)", "Prioriterte arter",
    "Andre spesielt hensynskrevende arter", "Ansvarsarter", "Atferd",
    "Merknader", "Lokalitet", "Dato", "Kjønn", "Innsamlingsdato/-tid",
    "Innsamler/Observatør",
]
existing_columns = hovedtabell_visning.columns.tolist() # Gets list of actual columns after renaming.
final_display_order = [col for col in preferred_display_order if col in existing_columns] # Filters preferred order by existing columns.
extra_columns = [col for col in existing_columns if col not in final_display_order] # Gets any remaining columns not in preferred list.
final_display_order.extend(extra_columns) # Adds extra columns to the end.

hovedtabell_visning = hovedtabell_visning[final_display_order] # Reorders columns. Assumes all columns in final_display_order exist.
st.dataframe(hovedtabell_visning, height=600, use_container_width=True) # Displays the main table.

# --- Display Section: Alien Species Table ---
st.subheader(
    f"Fremmede Arter (Basert på '{get_display_name(alien_col)}'='{alien_identifier}' eller '{get_display_name(category_col)}' i {category_identifiers})"
) # Subheader for alien species table.
fremmedart_tabell_visning = fremmede_arter_filtrert.copy() # Creates a copy for display modifications.
fremmedart_tabell_visning.columns = [get_display_name(col) for col in fremmedart_tabell_visning.columns] # Renames columns.
existing_alien_columns = [col for col in final_display_order if col in fremmedart_tabell_visning.columns] # Filters display order by existing alien columns.
fremmedart_tabell_visning = fremmedart_tabell_visning[existing_alien_columns] # Reorders columns. Assumes columns exist.
st.dataframe(fremmedart_tabell_visning, use_container_width=True) # Displays the alien species table.
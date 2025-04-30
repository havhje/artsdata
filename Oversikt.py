import streamlit as st
import pandas as pd
from pathlib import Path
from global_utils.column_mapping import get_display_name
from mapper_streamlit.landingsside.dashboard import display_dashboard  # Import the dashboard function
from global_utils.filter import display_filter_widgets, apply_filters  # Import filter functions

# Set page layout to wide
st.set_page_config(layout="wide")

st.title("Velkommen til artsanalyse")
st.write("Laget av Håvard Hjermstad-Sollerud")
st.subheader("Hva er dette?")
st.write(
    """Dette er en webapplikasjon som gjør at du kan se på data """
    """fra Artsdatabanken."""
)

# --- Define File Paths and Check Existence ---
# Define path relative to the current script file
# Broke path definition for readability
taxonomy_file = (
    Path(__file__).parent / "databehandling/output/Andøya_fugl_taxonomy.csv"
)
# Check if the direct file exists
use_direct_file = taxonomy_file.exists()  # Check if local taxonomy file exists

# --- File Loading Logic ---
# Initialize innlastet_data to ensure it's defined
innlastet_data = pd.DataFrame()

if use_direct_file:
    # Load taxonomy data directly if the file exists
    innlastet_data = pd.read_csv(taxonomy_file, delimiter=';')  # Load local CSV
else:
    # Otherwise, provide the file uploader
    st.subheader("Last opp fil")
    uploaded_file = st.file_uploader("Velg CSV-fil for taksonomi", type="csv")
    # Process only if a file is actually uploaded
    if uploaded_file is not None:
        # Load uploaded CSV
        innlastet_data = pd.read_csv(uploaded_file, delimiter=';')
    else:
        # Warning if local file missing and no upload yet
        st.warning("Lokal fil ikke funnet. Last opp en fil.")  # Show warning

# --- Filter Widgets --- Display filter options in the sidebar
display_filter_widgets(innlastet_data)

# --- Apply Filters --- Apply selected filters to get the data for display
data_for_visning = apply_filters(innlastet_data)

# --- Prepare Data for Dashboard ---
# Create a copy to avoid modifying the DataFrame used elsewhere
data_for_dashboard = data_for_visning.copy()
# Rename columns for display in the dashboard using the mapping function
data_for_dashboard.columns = [get_display_name(col) for col in data_for_dashboard.columns]

# --- Dashboard --- Display KPIs based on the FILTERED and RENAMED data
st.subheader("Nøkkeltall")  # Add a subheader for the dashboard
display_dashboard(data_for_dashboard)  # Call the dashboard function with the RENAMED data

# --- Define Alien Species Criteria ---
# Define columns and identifiers used for filtering (using ORIGINAL names on data_for_visning)
alien_col = "Fremmede arter"           # Original column name for the dedicated alien flag
category_col = "category"             # Original column name for Red List / Alien Risk category
alien_identifier = "Yes"            # Value indicating alien species in alien_col
# Values in category_col indicating alien species risk
category_identifiers = ['SE', 'HI', 'PH', 'LO']

# --- Pre-filter Data into Alien and Non-Alien Sets (Happy Path) ---
# Use the FILTERED data as the basis for separating alien/non-alien
fremmede_arter_filtrert = pd.DataFrame()    # Initialize empty DataFrame for alien species
ikke_fremmede_arter_filtrert = pd.DataFrame()  # Initialize empty DataFrame for non-alien species

# Calculate the condition for being an alien species (attempt even if data is empty)
# Check 'Fremmede arter' == 'Yes' OR category is SE, HI, PH, or LO
# NOTE: This will raise KeyError if data_for_visning is empty or columns are missing!
condition = (
    (data_for_visning[alien_col] == alien_identifier) |
    (data_for_visning[category_col].isin(category_identifiers))
)
# Separate the filtered data
# NOTE: This will also fail if the condition step failed.
# Apply filter for alien species using the filtered data
fremmede_arter_filtrert = data_for_visning[condition].copy()
# Apply inverse filter for non-alien species using the filtered data
ikke_fremmede_arter_filtrert = data_for_visning[~condition].copy()

# --- Display Section: Main Table (Non-Alien Species) ---
st.subheader("Hovedoversikt (Ikke-fremmede arter)")  # Update subheader

# Start main display with the filtered non-alien data (might be empty)
hovedtabell_visning = ikke_fremmede_arter_filtrert.copy()

# Rename columns using the mapping function
hovedtabell_visning.columns = [
    get_display_name(col) for col in hovedtabell_visning.columns
]

# List of preferred column display names in desired order
preferred_display_order = [
    # Core Identification
    "Taksonomisk Gruppe",
    "Orden",
    "Familie",
    "Art",
    "Antall Individer",
    "Kategori (Rødliste/Fremmedart)",
    "Prioriterte arter",
    "Andre spesielt hensynskrevende arter",
    "Ansvarsarter",
    "Atferd",
    "Merknader",
    "Lokalitet",
    "Dato",
    "Kjønn",
    "Innsamlingsdato/-tid",
    "Innsamler/Observatør",

    # Other potentially relevant columns can be added here if desired
]

# Get columns actually present in the DataFrame after renaming
existing_columns = hovedtabell_visning.columns.tolist()

# Create the final display order: take preferred columns that exist, then add any others
# Select existing columns from the preferred list
final_display_order = [col for col in preferred_display_order if col in existing_columns]
# Find columns present in data but not in preferred list
extra_columns = [col for col in existing_columns if col not in final_display_order]
# Add the extra columns to the end
final_display_order.extend(extra_columns)

# Reindex the DataFrame according to the final calculated order
# NOTE: This might raise KeyError if final_display_order contains columns not in hovedtabell_visning
hovedtabell_visning = hovedtabell_visning[final_display_order]

# Display the dataframe (might be empty)
st.dataframe(hovedtabell_visning, height=600)

# --- Section: Alien Species Table (if any) ---
# Check if there are any alien species found (now uses the filtered df)
if not fremmede_arter_filtrert.empty:  # Only display if the filtered alien DataFrame is not empty
    # Create a display copy, rename columns, and apply the same column order as the main table
    fremmedart_tabell_visning = fremmede_arter_filtrert.copy()  # Use .copy()
    fremmedart_tabell_visning.columns = [
        get_display_name(col) for col in fremmedart_tabell_visning.columns
    ]  # Rename columns
    # Ensure only columns present in this filtered data are used from final_display_order
    existing_alien_columns = [
        col for col in final_display_order if col in fremmedart_tabell_visning.columns
    ]  # Get existing columns in order
    fremmedart_tabell_visning = fremmedart_tabell_visning[
        existing_alien_columns
    ]  # Reindex using existing columns in the desired order

    # --- Display the Alien Species Table ---
    # Subheader for alien species
    st.subheader(
        "Fremmede Arter (Basert på Fremmede arter='Yes' eller Kategori='SE/HI/PH/LO')"
    )
    # Display the filtered, renamed, and reordered DataFrame
    st.dataframe(fremmedart_tabell_visning)

# Note: No explicit handling for missing columns or empty dataframes in this minimal version.

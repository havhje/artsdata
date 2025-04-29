import streamlit as st
import pandas as pd
from pathlib import Path
from global_utils.column_mapping import get_display_name

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
    Path(__file__).parent / "databehandling/output/fuglsortland_taxonomy.csv"
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
        innlastet_data = pd.read_csv(uploaded_file, delimiter=';')  # Load uploaded CSV
    else:
        # Warning if local file missing and no upload yet
        st.warning("Lokal fil ikke funnet. Last opp en fil.")  # Show warning

# --- Define Alien Species Criteria ---
# Define columns and identifiers used for filtering (assuming columns exist in original data)
alien_col = "Fremmede arter"           # Original column name for the dedicated alien flag
category_col = "category"             # Original column name for Red List / Alien Risk category
alien_identifier = "Yes"            # Value indicating alien species in alien_col
category_identifiers = ['SE', 'HI', 'PH', 'LO'] # Values in category_col indicating alien species risk

# --- Pre-filter Data into Alien and Non-Alien Sets (Happy Path) ---
fremmede_arter_filtrert = pd.DataFrame()    # Initialize empty DataFrame for alien species
ikke_fremmede_arter_filtrert = pd.DataFrame() # Initialize empty DataFrame for non-alien species

if not innlastet_data.empty: # Proceed only if data was loaded
    # Calculate the condition for being an alien species (assuming columns exist)
    condition = (
        (innlastet_data[alien_col] == alien_identifier) | # Check 'Fremmede arter' == 'Yes'
        (innlastet_data[category_col].isin(category_identifiers)) # Check category is SE, HI, PH, or LO
    )
    # Separate the original data
    fremmede_arter_filtrert = innlastet_data[condition].copy()     # Apply filter for alien species
    ikke_fremmede_arter_filtrert = innlastet_data[~condition].copy() # Apply inverse filter for non-alien species
else:
    # If no data loaded, assign the (empty) innlastet_data to non-alien to avoid errors later
    ikke_fremmede_arter_filtrert = innlastet_data

# --- Display Section: Main Table (Non-Alien Species) ---
st.subheader("Hovedoversikt (Ikke-fremmede arter)") # Update subheader

hovedtabell_visning = ikke_fremmede_arter_filtrert.copy() # Start main display with non-alien data

# Rename columns using the mapping function
hovedtabell_visning.columns = [get_display_name(col) for col in hovedtabell_visning.columns]

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
hovedtabell_visning = hovedtabell_visning[final_display_order]

st.dataframe(hovedtabell_visning, height=600)  # Display the dataframe with custom column order and increased height

# --- Section: Alien Species Table (if any) ---
# Check if there are any alien species found
if not fremmede_arter_filtrert.empty: # Only display if the filtered alien DataFrame is not empty
    # Create a display copy, rename columns, and apply the same column order as the main table
    fremmedart_tabell_visning = fremmede_arter_filtrert # Assign filtered data to new display df
    fremmedart_tabell_visning.columns = [get_display_name(col) for col in fremmedart_tabell_visning.columns] # Rename columns
    # Ensure only columns present in this filtered data are used from final_display_order
    existing_alien_columns = [col for col in final_display_order if col in fremmedart_tabell_visning.columns] # Get existing columns in order
    fremmedart_tabell_visning = fremmedart_tabell_visning[existing_alien_columns] # Reindex using existing columns in the desired order

    # --- Display the Alien Species Table ---
    st.subheader("Fremmede Arter (Basert på Fremmede arter='Yes' eller Kategori='SE/HI/PH/LO')") # Subheader for alien species
    st.dataframe(fremmedart_tabell_visning) # Display the filtered, renamed, and reordered DataFrame

# Note: No explicit handling for missing columns in this minimal version.

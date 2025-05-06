# ##### Imports #####
import pandas as pd # Import pandas for data manipulation.
import streamlit as st # Import Streamlit for caching.

# ##### Constants #####
REDLIST_CATEGORIES = ['CR', 'EN', 'VU', 'NT', 'DD'] # Define redlist categories. Modifying affects counts.
ALIEN_CATEGORIES_LIST = ['SE', 'HI', 'PH', 'LO'] # Define specific alien risk categories.
SPECIAL_STATUS_COLS = ["Prioriterte Arter", "Andre Spes. Hensyn.", "Ansvarsarter", "Spes. Økol. Former"] # Define special status column names.

# ##### Calculation Functions #####

# --- Function: calculate_all_status_counts ---
# Calculates counts for Red List, Alien Species, and other special status categories.
# Takes a pandas DataFrame 'data'.
# Returns a dictionary containing various status counts.
@st.cache_data
def calculate_all_status_counts(data):
    # --- Red List Counts ---
    # Assumes standard category codes exist in the renamed columns.
    category_col = "Kategori (Rødliste/Fremmedart)" # Define the main category column name.
    # Count rows matching any redlist categories (Total).
    redlisted_total_count = data[category_col].isin(REDLIST_CATEGORIES).sum()

    # Calculate count for each specific red list category.
    redlist_counts_individual = {} # Initialize dictionary to store counts per category.
    for category in REDLIST_CATEGORIES: # Iterate through the defined categories.
        # Count rows where the category column exactly matches the current category.
        redlist_counts_individual[category] = (data[category_col] == category).sum()

    # --- Alien Species Counts ---
    alien_yes_col = "Fremmede arter kategori" # Define the dedicated 'Yes' column name for aliens.

    is_alien_category = data[category_col].isin(ALIEN_CATEGORIES_LIST)  # Check category column for risk codes.
    is_alien_yes = data[alien_yes_col] == 'Yes'  # Check dedicated 'Yes' column.
    alien_total_count = (is_alien_category | is_alien_yes).sum()  # Total alien count (either condition is true).

    # Calculate counts for each breakdown risk category
    alien_counts_individual = {} # Dictionary to store breakdown counts.
    for category in ALIEN_CATEGORIES_LIST: # Iterate through risk categories.
        alien_counts_individual[category] = (data[category_col] == category).sum() # Count matches in category column.

    # --- Other Special Status Counts ---
    special_status_counts = {} # Dictionary to store counts for other statuses.
    for status_col in SPECIAL_STATUS_COLS: # Iterate through the status column names.
        special_status_counts[status_col] = (data[status_col] == 'Yes').sum() # Count 'Yes' in the respective column.

    # Calculate Total for Special Status Section Title
    # Sum the individual 'Yes' counts calculated above.
    total_special_status_count = sum(special_status_counts.values())

    counts = { # Package results into a dictionary.
        "redlist_total": redlisted_total_count,
        "redlist_breakdown": redlist_counts_individual,
        "alien_total": alien_total_count,
        "alien_breakdown": alien_counts_individual,
        "special_status_breakdown": special_status_counts,
        "special_status_total": total_special_status_count,
        # Include constants lists for reference by display functions if needed
        "redlist_categories_order": REDLIST_CATEGORIES,
        "alien_categories_order": ALIEN_CATEGORIES_LIST,
        "special_status_cols_order": SPECIAL_STATUS_COLS,
    }
    return counts # Return the dictionary of status counts. 
# ##### Imports #####
import pandas as pd # Import pandas for data manipulation.
import streamlit as st # Import Streamlit for caching.

# ##### Constants #####
REDLIST_CATEGORIES = ['CR', 'EN', 'VU', 'NT', 'DD'] # Define redlist categories. Modifying affects counts.
ALIEN_CATEGORIES_LIST = ['SE', 'HI', 'PH', 'LO'] # Define specific alien risk categories.
# SPECIAL_STATUS_COLS removed, will be passed as a parameter list of original names

# ##### Calculation Functions #####

# --- Function: calculate_all_status_counts ---
# Calculates counts for Red List, Alien Species, and other special status categories.
# Takes a pandas DataFrame 'data' and relevant original column names.
# Returns a dictionary containing various status counts.
@st.cache_data
def calculate_all_status_counts(data,
                                category_col: str,           # Original column name for Red List/Alien Risk category
                                alien_flag_col: str,         # Original column name for the 'Yes' flag for alien species
                                original_special_status_cols: list # List of original column names for special statuses
                                ):
    # --- Red List Counts ---
    # Assumes standard category codes exist in the original category column.
    # category_col is now a parameter (original name)
    # Count rows matching any redlist categories (Total).
    redlisted_total_count = data[category_col].isin(REDLIST_CATEGORIES).sum()

    # Calculate count for each specific red list category.
    redlist_counts_individual = {} # Initialize dictionary to store counts per category.
    for category_value in REDLIST_CATEGORIES: # Iterate through the defined categories.
        # Count rows where the category column exactly matches the current category_value.
        redlist_counts_individual[category_value] = (data[category_col] == category_value).sum()

    # --- Alien Species Counts ---
    # alien_flag_col is now a parameter (original name for 'Fremmede arter' type column)

    is_alien_category = data[category_col].isin(ALIEN_CATEGORIES_LIST)  # Check category column for risk codes.
    is_alien_yes = data[alien_flag_col].astype(str).str.upper() == 'YES'  # Check dedicated alien flag column (original name), ensure robust comparison.
    alien_total_count = (is_alien_category | is_alien_yes).sum()  # Total alien count (either condition is true).

    # Calculate counts for each breakdown risk category
    alien_counts_individual = {} # Dictionary to store breakdown counts.
    for category_value in ALIEN_CATEGORIES_LIST: # Iterate through risk categories.
        alien_counts_individual[category_value] = (data[category_col] == category_value).sum() # Count matches in category column.

    # --- Other Special Status Counts ---
    special_status_counts = {} # Dictionary to store counts for other statuses.
    for original_status_col_name in original_special_status_cols: # Iterate through the original status column names.
        # Count 'Yes' (case-insensitive) in the respective original status column.
        # Ensure the column is treated as string for robust 'Yes' check
        if original_status_col_name in data.columns:
            special_status_counts[original_status_col_name] = (data[original_status_col_name].astype(str).str.upper() == 'YES').sum()
        else:
            special_status_counts[original_status_col_name] = 0 # If column somehow missing, count as 0

    # Calculate Total for Special Status Section Title
    # Sum the individual 'Yes' counts calculated above.
    total_special_status_count = sum(special_status_counts.values())

    counts = { # Package results into a dictionary.
        "redlist_total": redlisted_total_count,
        "redlist_breakdown": redlist_counts_individual,
        "alien_total": alien_total_count,
        "alien_breakdown": alien_counts_individual,
        "special_status_breakdown": special_status_counts, # Keys are original special status col names
        "special_status_total": total_special_status_count,
        # Include constants lists for reference by display functions if needed
        "redlist_categories_order": REDLIST_CATEGORIES,
        "alien_categories_order": ALIEN_CATEGORIES_LIST,
        "special_status_cols_order": original_special_status_cols, # Now contains original names
    }
    return counts # Return the dictionary of status counts. 
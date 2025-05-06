# ##### Imports #####
import pandas as pd # Import pandas for data manipulation and aggregation.
import streamlit as st # Import Streamlit for caching.

# ##### Constants #####
# These are duplicated from status counts but useful here for iterating
REDLIST_CATEGORIES = ['CR', 'EN', 'VU', 'NT', 'DD'] # Define redlist categories.
ALIEN_CATEGORIES_LIST = ['SE', 'HI', 'PH', 'LO'] # Define specific alien risk categories.
# SPECIAL_STATUS_COLS and CATEGORY_COL removed, will be passed as parameters

# ##### Calculation Functions #####

# --- Function: _prepare_data_for_top_lists ---
# Helper function to ensure the numeric individual count column exists.
# Takes a pandas DataFrame 'data' and the original name of the individual count column.
# Returns the DataFrame with a standardized numeric individual count column 'Antall Individer Num'.
# Note: The output column 'Antall Individer Num' is a processing column; its name is kept generic here.
# If this also needs to be an original name, the function signature would need to change further.
def _prepare_data_for_top_lists(data, original_individual_count_col: str):
    data_copy = data.copy() # Work on a copy to avoid SettingWithCopyWarning.
    # Ensure original individual count column is numeric for calculations, store in 'Antall Individer Num'.
    data_copy['Antall Individer Num'] = pd.to_numeric(data_copy[original_individual_count_col], errors='coerce').fillna(0)
    return data_copy # Return the modified copy.

# --- Function: calculate_all_top_lists ---
# Calculates various Top N lists based on frequency and individual counts.
# Takes a pandas DataFrame 'data', original column names, and optional 'top_n' integer.
# Returns a dictionary containing all calculated top list DataFrames (with original column names).
@st.cache_data
def calculate_all_top_lists(data, # Non-default parameters first
                            art_col: str,                  # Original column name for species
                            family_col: str,               # Original column name for family
                            observer_col: str,             # Original column name for observer
                            individual_count_col: str,   # Original column name for individual counts
                            category_col: str,             # Original column name for Red List/Alien Risk category
                            original_special_status_cols: list, # List of original column names for special statuses
                            top_n=10                       # Default parameter at the end
                            ):
    if data.empty: # Handle empty input DataFrame early.
        # Return a dictionary with empty DataFrames/structures matching expected output keys
        # Column names here should reflect the original names that would be present in populated DFs.
        return {
            "top_species_freq": pd.DataFrame(columns=[art_col, 'Antall_Observasjoner']),
            "top_families_freq": pd.DataFrame(columns=[family_col, 'Antall_Observasjoner']),
            "top_observers_freq": pd.DataFrame(columns=[observer_col, 'Antall_Observasjoner']),
            # For top_individual_obs, columns will be original data columns + 'Antall Individer Num'
            "top_individual_obs": pd.DataFrame(columns=data.columns.tolist() + ['Antall Individer Num'] if not data.columns.empty else ['Antall Individer Num']),
            "top_redlist_species_agg": {cat_val: pd.DataFrame(columns=[art_col, 'Antall_Observasjoner', 'Sum_Individer']) for cat_val in REDLIST_CATEGORIES},
            "top_alien_species_agg": {cat_val: pd.DataFrame(columns=[art_col, 'Antall_Observasjoner', 'Sum_Individer']) for cat_val in ALIEN_CATEGORIES_LIST},
            "top_special_species_agg": {orig_status_col: pd.DataFrame(columns=[art_col, 'Antall_Observasjoner', 'Sum_Individer']) for orig_status_col in original_special_status_cols},
        }

    data = _prepare_data_for_top_lists(data, individual_count_col) # Ensure numeric individual count column exists.

    # --- Basic Frequency Top Lists ---
    # Top Species by Frequency (Simple Count)
    top_species = data[art_col].value_counts().nlargest(top_n).reset_index() # Calculate top N species by count.
    top_species.columns = [art_col, 'Antall_Observasjoner'] # Rename columns (art_col is original, second is generic count name).

    # Top Families by Frequency (Simple Count)
    top_families = data[family_col].value_counts().nlargest(top_n).reset_index() # Calculate top N families by count.
    top_families.columns = [family_col, 'Antall_Observasjoner'] # Rename columns.

    # Top Observers by Frequency (Simple Count)
    top_observers = data[observer_col].value_counts().nlargest(top_n).reset_index() # Calculate top N observers.
    top_observers.columns = [observer_col, "Antall_Observasjoner"] # Rename columns.

    # --- Top Observations by Individual Count ---
    # Get the top N rows based on the numeric individual count.
    top_individual_obs = data.nlargest(top_n, 'Antall Individer Num') # Uses the processing column.

    # --- Category-Specific Top Lists (Frequency & Sum Individuals) ---
    # Red List Species Aggregated per Category
    top_redlist_species_by_cat = {} # Dict to store DataFrames for each category.
    for category_value in REDLIST_CATEGORIES: # Loop through CR, EN, etc.
        category_data = data[data[category_col] == category_value] # Filter data for this category using original category_col.
        if not category_data.empty:
            agg_df = category_data.groupby(art_col).agg(
                Antall_Observasjoner=(art_col, 'size'), # Count observations per species.
                Sum_Individer=('Antall Individer Num', 'sum') # Sum individuals per species.
            ).reset_index() # Reset index to make art_col a column.
            agg_df_sorted = agg_df.sort_values(by=['Antall_Observasjoner', 'Sum_Individer'], ascending=[False, False])
            top_redlist_species_by_cat[category_value] = agg_df_sorted.head(top_n)
        else:
            top_redlist_species_by_cat[category_value] = pd.DataFrame(columns=[art_col, 'Antall_Observasjoner', 'Sum_Individer'])

    # Alien Species Aggregated per Category
    top_alien_species_by_cat = {} # Dict to store DataFrames for each category.
    for category_value in ALIEN_CATEGORIES_LIST: # Loop through SE, HI, etc.
        category_data = data[data[category_col] == category_value] # Filter data for this risk category.
        if not category_data.empty:
            agg_df = category_data.groupby(art_col).agg(
                Antall_Observasjoner=(art_col, 'size'), # Frequency.
                Sum_Individer=('Antall Individer Num', 'sum') # Sum of individuals.
            ).reset_index()
            agg_df_sorted = agg_df.sort_values(by=['Antall_Observasjoner', 'Sum_Individer'], ascending=[False, False])
            top_alien_species_by_cat[category_value] = agg_df_sorted.head(top_n)
        else:
            top_alien_species_by_cat[category_value] = pd.DataFrame(columns=[art_col, 'Antall_Observasjoner', 'Sum_Individer'])

    # Special Status Species Aggregated per Column
    top_special_species_by_col = {} # Dict to store DataFrames for each status.
    for original_status_col_name in original_special_status_cols: # Loop through the original status column names.
        status_data = data[data[original_status_col_name].astype(str).str.upper() == 'YES'] # Filter data where this status is 'Yes'.
        if not status_data.empty:
            agg_df = status_data.groupby(art_col).agg(
                Antall_Observasjoner=(art_col, 'size'), # Frequency.
                Sum_Individer=('Antall Individer Num', 'sum') # Sum of individuals.
            ).reset_index()
            agg_df_sorted = agg_df.sort_values(by=['Antall_Observasjoner', 'Sum_Individer'], ascending=[False, False])
            top_special_species_by_col[original_status_col_name] = agg_df_sorted.head(top_n)
        else:
            top_special_species_by_col[original_status_col_name] = pd.DataFrame(columns=[art_col, 'Antall_Observasjoner', 'Sum_Individer'])

    top_lists_result = { # Package results into a dictionary.
        "top_species_freq": top_species, # DF columns: [art_col, 'Antall_Observasjoner']
        "top_families_freq": top_families, # DF columns: [family_col, 'Antall_Observasjoner']
        "top_observers_freq": top_observers, # DF columns: [observer_col, 'Antall_Observasjoner']
        "top_individual_obs": top_individual_obs, # DF columns: original data cols + 'Antall Individer Num'
        "top_redlist_species_agg": top_redlist_species_by_cat, # DFs with [art_col, 'Antall_Observasjoner', 'Sum_Individer']
        "top_alien_species_agg": top_alien_species_by_cat,   # DFs with [art_col, 'Antall_Observasjoner', 'Sum_Individer']
        "top_special_species_agg": top_special_species_by_col # DFs with [art_col, 'Antall_Observasjoner', 'Sum_Individer']
    }
    return top_lists_result # Return the dictionary of top list DataFrames. 
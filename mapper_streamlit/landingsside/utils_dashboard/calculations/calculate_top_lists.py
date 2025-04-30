# ##### Imports #####
import pandas as pd # Import pandas for data manipulation and aggregation.

# ##### Constants #####
# These are duplicated from status counts but useful here for iterating
REDLIST_CATEGORIES = ['CR', 'EN', 'VU', 'NT', 'DD'] # Define redlist categories.
ALIEN_CATEGORIES_LIST = ['SE', 'HI', 'PH', 'LO'] # Define specific alien risk categories.
SPECIAL_STATUS_COLS = ["Prioriterte Arter", "Andre Spes. Hensyn.", "Ansvarsarter", "Spes. Økol. Former"] # Define special status column names.
CATEGORY_COL = "Kategori (Rødliste/Fremmedart)" # Define the main category column name.

# ##### Calculation Functions #####

# --- Function: _prepare_data_for_top_lists ---
# Helper function to ensure the numeric individual count column exists.
# Takes a pandas DataFrame 'data'.
# Returns the DataFrame with 'Antall Individer Num' added/updated.
def _prepare_data_for_top_lists(data):
    data_copy = data.copy() # Work on a copy to avoid SettingWithCopyWarning.
    # Ensure 'Antall Individer' is numeric for calculations, store in new column.
    data_copy['Antall Individer Num'] = pd.to_numeric(data_copy['Antall Individer'], errors='coerce').fillna(0)
    return data_copy # Return the modified copy.

# --- Function: calculate_all_top_lists ---
# Calculates various Top N lists based on frequency and individual counts.
# Takes a pandas DataFrame 'data' and optional 'top_n' integer.
# Returns a dictionary containing all calculated top list DataFrames.
def calculate_all_top_lists(data, top_n=10):
    if data.empty: # Handle empty input DataFrame early.
        # Return a dictionary with empty DataFrames/structures matching expected output keys
        return {
            "top_species_freq": pd.DataFrame(columns=['Art', 'Antall_Observasjoner']),
            "top_families_freq": pd.DataFrame(columns=['Familie', 'Antall_Observasjoner']),
            "top_observers_freq": pd.DataFrame(columns=['Innsamler/Observatør', 'Antall Observasjoner']),
            "top_individual_obs": pd.DataFrame(columns=data.columns.tolist() + ['Antall Individer Num']), # Include original cols + numeric
            "top_redlist_species_agg": {cat: pd.DataFrame(columns=['Art', 'Antall_Observasjoner', 'Sum_Individer']) for cat in REDLIST_CATEGORIES},
            "top_alien_species_agg": {cat: pd.DataFrame(columns=['Art', 'Antall_Observasjoner', 'Sum_Individer']) for cat in ALIEN_CATEGORIES_LIST},
            "top_special_species_agg": {col: pd.DataFrame(columns=['Art', 'Antall_Observasjoner', 'Sum_Individer']) for col in SPECIAL_STATUS_COLS},
        }

    data = _prepare_data_for_top_lists(data) # Ensure numeric individual count column exists.

    # --- Basic Frequency Top Lists ---
    # Top Species by Frequency (Simple Count)
    top_species = data['Art'].value_counts().nlargest(top_n).reset_index() # Calculate top N species by count.
    top_species.columns = ['Art', 'Antall_Observasjoner'] # Rename columns for clarity.

    # Top Families by Frequency (Simple Count)
    top_families = data['Familie'].value_counts().nlargest(top_n).reset_index() # Calculate top N families by count.
    top_families.columns = ['Familie', 'Antall_Observasjoner'] # Rename columns for clarity.

    # Top Observers by Frequency (Simple Count)
    top_observers = data["Innsamler/Observatør"].value_counts().nlargest(top_n).reset_index() # Calculate top N observers.
    top_observers.columns = ["Innsamler/Observatør", "Antall Observasjoner"] # Rename columns for clarity.

    # --- Top Observations by Individual Count ---
    # Get the top N rows based on the numeric individual count.
    top_individual_obs = data.nlargest(top_n, 'Antall Individer Num')

    # --- Category-Specific Top Lists (Frequency & Sum Individuals) ---
    # Red List Species Aggregated per Category
    top_redlist_species_by_cat = {} # Dict to store DataFrames for each category.
    for category in REDLIST_CATEGORIES: # Loop through CR, EN, etc.
        category_data = data[data[CATEGORY_COL] == category] # Filter data for this category.
        if not category_data.empty:
            # Group by Art, count occurrences (frequency), and sum individuals.
            agg_df = category_data.groupby('Art').agg(
                Antall_Observasjoner=('Art', 'size'), # Count observations per species.
                Sum_Individer=('Antall Individer Num', 'sum') # Sum individuals per species.
            ).reset_index() # Reset index to make 'Art' a column.
            # Get top N based on observation frequency and store.
            top_redlist_species_by_cat[category] = agg_df.nlargest(top_n, 'Antall_Observasjoner')
        else:
            # Store an empty DataFrame if no data for this category.
            top_redlist_species_by_cat[category] = pd.DataFrame(columns=['Art', 'Antall_Observasjoner', 'Sum_Individer'])

    # Alien Species Aggregated per Category
    top_alien_species_by_cat = {} # Dict to store DataFrames for each category.
    for category in ALIEN_CATEGORIES_LIST: # Loop through SE, HI, etc.
        category_data = data[data[CATEGORY_COL] == category] # Filter data for this risk category.
        if not category_data.empty:
            # Group by Art, count occurrences, sum individuals.
            agg_df = category_data.groupby('Art').agg(
                Antall_Observasjoner=('Art', 'size'), # Frequency.
                Sum_Individer=('Antall Individer Num', 'sum') # Sum of individuals.
            ).reset_index()
            # Get top N based on frequency and store.
            top_alien_species_by_cat[category] = agg_df.nlargest(top_n, 'Antall_Observasjoner')
        else:
            # Store an empty DataFrame if no data for this category.
            top_alien_species_by_cat[category] = pd.DataFrame(columns=['Art', 'Antall_Observasjoner', 'Sum_Individer'])

    # Special Status Species Aggregated per Column
    top_special_species_by_col = {} # Dict to store DataFrames for each status.
    for status_col in SPECIAL_STATUS_COLS: # Loop through the status column names.
        status_data = data[data[status_col] == 'Yes'] # Filter data where this status is 'Yes'.
        if not status_data.empty:
            # Group by Art, count occurrences, sum individuals.
            agg_df = status_data.groupby('Art').agg(
                Antall_Observasjoner=('Art', 'size'), # Frequency.
                Sum_Individer=('Antall Individer Num', 'sum') # Sum of individuals.
            ).reset_index()
            # Get top N based on frequency and store.
            top_special_species_by_col[status_col] = agg_df.nlargest(top_n, 'Antall_Observasjoner')
        else:
             # Store an empty DataFrame if no data for this status.
            top_special_species_by_col[status_col] = pd.DataFrame(columns=['Art', 'Antall_Observasjoner', 'Sum_Individer'])

    top_lists = { # Package results into a dictionary.
        "top_species_freq": top_species,
        "top_families_freq": top_families,
        "top_observers_freq": top_observers,
        "top_individual_obs": top_individual_obs,
        "top_redlist_species_agg": top_redlist_species_by_cat,
        "top_alien_species_agg": top_alien_species_by_cat,
        "top_special_species_agg": top_special_species_by_col,
    }
    return top_lists # Return the dictionary of top list DataFrames. 
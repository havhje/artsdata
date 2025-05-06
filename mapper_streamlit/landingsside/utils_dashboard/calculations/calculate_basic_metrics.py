# ##### Imports #####
import pandas as pd # Import pandas for data manipulation.
import streamlit as st # Import Streamlit for caching.

# ##### Calculation Functions #####

# --- Function: calculate_basic_metrics ---
# Calculates basic summary statistics from the observation data.
# Takes a pandas DataFrame 'data' and original column names.
# Returns a dictionary containing total records, individuals, unique counts, and date range.
@st.cache_data
def calculate_basic_metrics(data,
                            individual_count_col: str, # Original column name for individual counts
                            art_col: str,             # Original column name for species
                            family_col: str,          # Original column name for family
                            observer_col: str,        # Original column name for observer
                            event_date_col: str       # Original column name for event date
                            ):
    # Basic Counts & Sums
    total_records = len(data)  # Get total number of observations. Filter changes affect this.
    # Sum individuals, coercing errors to 0. Safer than direct sum.
    total_individuals = pd.to_numeric(data[individual_count_col], errors='coerce').fillna(0).astype(int).sum()
    unique_species = data[art_col].nunique()  # Count unique species names using original column.
    unique_families = data[family_col].nunique()  # Count unique family names using original column.
    unique_observers = data[observer_col].nunique()  # Count unique observer names using original column.

    # Date Range
    # Convert to datetime, coercing errors to NaT (Not a Time).
    # REMOVED the strict format string to handle various input formats or pre-parsed dates.
    valid_dates = pd.to_datetime(
        data[event_date_col], 
        errors='coerce' 
        # format='%d.%m.%Y %H:%M:%S' # REMOVED strict format
    ).dropna()
    min_date = valid_dates.min() if not valid_dates.empty else None  # Get earliest date if available.
    max_date = valid_dates.max() if not valid_dates.empty else None  # Get latest date if available.

    metrics = { # Package results into a dictionary.
        "total_records": total_records,
        "total_individuals": total_individuals,
        "unique_species": unique_species,
        "unique_families": unique_families,
        "unique_observers": unique_observers,
        "min_date": min_date,
        "max_date": max_date,
    }
    return metrics # Return the dictionary of calculated metrics.

# ##### Imports #####
import pandas as pd # Import pandas for data manipulation.
import streamlit as st # Import Streamlit for caching.

# ##### Calculation Functions #####

# --- Function: calculate_basic_metrics ---
# Calculates basic summary statistics from the observation data.
# Takes a pandas DataFrame 'data'.
# Returns a dictionary containing total records, individuals, unique counts, and date range.
@st.cache_data
def calculate_basic_metrics(data):
    # Basic Counts & Sums
    total_records = len(data)  # Get total number of observations. Filter changes affect this.
    # Sum individuals, coercing errors to 0. Safer than direct sum.
    total_individuals = pd.to_numeric(data["Antall Individer"], errors='coerce').fillna(0).astype(int).sum()
    unique_species = data["Art"].nunique()  # Count unique species names.
    unique_families = data["Familie"].nunique()  # Count unique family names.
    unique_observers = data["Innsamler/Observatør"].nunique()  # Count unique observer names.

    # Date Range
    # Convert to datetime, coercing errors to NaT (Not a Time).
    # Explicitly specify the expected date format to avoid warnings and ensure correct parsing.
    valid_dates = pd.to_datetime(
        data["Innsamlingsdato/-tid"], 
        errors='coerce', 
        format='%d.%m.%Y %H:%M:%S' # Specify expected day-first format with time
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

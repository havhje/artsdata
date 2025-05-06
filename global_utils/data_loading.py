# global_utils/data_loader.py
##### Imports #####
import streamlit as st # Used for caching decorator.
import pandas as pd # Used for DataFrame creation and manipulation.
# import numpy as np # Not needed if using errors='coerce'

##### Constants #####
# Define columns expected to be numeric, based ONLY on fuglsortland_taxonomy.csv header.
# Assumes these columns exist. Modifying this list changes which columns are processed.
NUMERIC_COLUMNS = [
    "individualCount",                # This column name is present in the CSV header.
    "latitude",                       # This column name is present in the CSV header. Uses comma decimal.
    "longitude",                      # This column name is present in the CSV header. Uses comma decimal.
    "coordinateUncertaintyInMeters", # This column name is present in the CSV header. Assumes period decimal or integer.
]

# Define columns expected to be dates, with their respective parsing formats, based ONLY on fuglsortland_taxonomy.csv header.
# Assumes this column exists and data matches the specified format. Modifying this dict changes which columns are processed and how.
DATE_COLUMNS_FORMATS = {
    "dateTimeCollected": "%d.%m.%Y %H:%M:%S", # This column name is present in the CSV header. Expected format DD.MM.YYYY HH:MM:SS.
}

##### Functions #####
@st.cache_data # Caches the output. Re-runs use cached data if input is unchanged. Improves performance for repeated loads of the same file.
def load_and_prepare_data(file_input): # Loads data from CSV and performs minimal preprocessing. Assumes file_input is valid path/buffer and columns exist.
    # --- Load Data ---
    # Reads the CSV file using the provided path or buffer. Assumes ';' delimiter and that the file loads successfully.
    df = pd.read_csv(file_input, delimiter=';') # Loads data into a pandas DataFrame. Failure here will raise an exception.

    # --- Perform Minimal Preprocessing Steps ---

    # --- Convert Numeric Columns ---
    # Iterates through the columns listed in NUMERIC_COLUMNS. Assumes each column exists in df.
    for col in NUMERIC_COLUMNS: # Loop through the predefined numeric column names.
        # Convert column to string, replace comma decimal with period, then convert to numeric.
        # *** ADDED errors='coerce' *** Handles non-numeric strings (like "nan") by converting them to NaN.
        numeric_series = pd.to_numeric(df[col].astype(str).str.replace(',', '.', regex=False), errors='coerce') # Replaces ',' with '.', converts, coerces errors to NaN.
        df[col] = numeric_series # Assign the converted series (potentially with NaNs) back to the DataFrame column.

        if col == "individualCount": # Specific handling for 'individualCount'. Assumes it exists.
            # Check if the column actually contains numbers after coercion before attempting cast
            if numeric_series.notna().any(): # Check if there are any non-NaN values after coercion.
               try: # Add try-except for the strict Int64Dtype conversion
                   df[col] = numeric_series.astype(pd.Int64Dtype()) # Converts to nullable integer type. NaNs remain NaNs.
               except TypeError: # Handle case where even after coerce, type cannot be cast (e.g., float NaNs sometimes cause issues)
                   pass # Keep the numeric (float) type if Int64 casting fails

    # --- Convert Date/Time Columns ---
    # Iterates through the date columns listed in DATE_COLUMNS_FORMATS. Assumes each column exists in df.
    for col, fmt in DATE_COLUMNS_FORMATS.items(): # Loop through the predefined date column names and their formats.
        # Converts the column to datetime objects using the specified format. Assumes data matches the format; mismatches will raise an error.
        # *** Consider adding errors='coerce' here too for robustness ***
        df[col] = pd.to_datetime(df[col].astype(str), format=fmt, errors='coerce') # Converts first to string, then to datetime. Coerce date errors.

    # --- Strip Whitespace from Object (String) Columns ---
    # Iterates through all columns identified by pandas as 'object' dtype (usually strings).
    for col_name in df.select_dtypes(include=['object']).columns: # Select columns likely containing strings.
        # Removes leading/trailing whitespace from string data in the column. Assumes the column contains string-like data amenable to .str accessor.
         if isinstance(df[col_name].dtype, pd.StringDtype) or df[col_name].apply(type).eq(str).any(): # Check if strings present before strip
             df[col_name] = df[col_name].str.strip() # Applies string strip operation.


    # --- Geometry Parsing (Placeholder) ---
    # No geometry parsing implemented in this minimal version. Column 'geometry' remains as read from CSV.

    return df # Returns the preprocessed DataFrame, now with NaN for unparseable numbers.
# ##### Imports #####
import pandas as pd  # Import pandas for data manipulation.
import logging      # Import logging module.
import streamlit as st # Import Streamlit for caching.

# --- Setup Logging ---
# Get a logger instance for this module.
logger = logging.getLogger(__name__)

# ##### Calculation Function #####

@st.cache_data
def calculate_yearly_metrics(data, date_col_name: str, individuals_col_name: str):
    # --- Function: calculate_yearly_metrics ---
    # Calculates yearly sums of observations and individuals, and the average individuals per observation.
    # Takes the DataFrame, the name of the date column, and the name of the individuals column.
    # Returns an empty DataFrame if required columns are missing or other KeyErrors occur.

    # --- Define expected output columns for empty DataFrame case ---
    output_columns = ['Year', 'Sum_Observations', 'Sum_Individuals', 'Avg_Individuals_Per_Observation']

    # --- Initial Check (Optional but good practice) ---
    # Quick check if input is empty or not a DataFrame, return early.
    if not isinstance(data, pd.DataFrame) or data.empty:
        logger.warning("Input data is not a DataFrame or is empty. Returning empty yearly metrics.")  # Log warning.
        return pd.DataFrame(columns=output_columns)  # Return empty df.

    # --- Core Calculation with Error Handling ---
    try:
        # Check if required columns exist before processing using the provided names.
        if date_col_name not in data.columns:
            # Log specific error.
            logger.error(f"Required date column '{date_col_name}' not found in input data. "
                         f"Returning empty yearly metrics.")
            return pd.DataFrame(columns=output_columns)  # Return empty df.
        if individuals_col_name not in data.columns:
            # Log specific error.
            logger.error(f"Required individuals column '{individuals_col_name}' not found in input data. "
                         f"Returning empty yearly metrics.")
            return pd.DataFrame(columns=output_columns)  # Return empty df.

        # --- Data Preparation ---
        df = data.copy()  # Create a copy.
        # Convert date column to datetime objects.
        # Removing the strict format string allows pandas to infer the format or handle already-datetime objects.
        # errors='coerce' will turn unparseable dates into NaT.
        df[date_col_name] = pd.to_datetime(
            df[date_col_name], 
            errors='coerce' 
            # format='%d.%m.%Y %H:%M:%S' # Strict format string removed for flexibility
        )
        df.dropna(subset=[date_col_name], inplace=True)  # Drop rows where date conversion resulted in NaT.

        # Handle empty DataFrame after date conversion/dropna
        if df.empty:
            # Log warning.
            logger.warning("DataFrame became empty after date conversion/dropping NaTs. "
                         "Returning empty yearly metrics.")
            return pd.DataFrame(columns=output_columns)  # Return empty df.

        df['Year'] = df[date_col_name].dt.year  # Extract year.

        # --- Aggregation ---
        # Group by year and aggregate using the provided individuals column name.
        yearly_summary = df.groupby('Year').agg(
            Sum_Observations=('Year', 'size'),                      # Count observations.
            Sum_Individuals=(individuals_col_name, 'sum')         # Sum individuals using the provided column name.
        ).reset_index()  # Reset index to make 'Year' a column.

        # --- Calculate Average Individuals per Observation --- # Compute the mean individuals for each year
        yearly_summary['Avg_Individuals_Per_Observation'] = (
            yearly_summary['Sum_Individuals'] / yearly_summary['Sum_Observations'] # Perform division
        )
        # Fill NaN values (results of 0/0 division) with 0. Assign result back.
        yearly_summary['Avg_Individuals_Per_Observation'] = (
            yearly_summary['Avg_Individuals_Per_Observation'].fillna(0)
        )

        # --- Return Result --- # Return the calculated yearly metrics.
        return yearly_summary

    except KeyError as e:
        # Catch potential KeyErrors during processing (e.g., unforeseen column issues)
        # Log the error and available columns.
        logger.error(f"A KeyError occurred during yearly metric calculation: {e}. "
                    f"Columns available: {list(data.columns)}. Returning empty yearly metrics.")
        return pd.DataFrame(columns=output_columns)  # Return empty df.
    except Exception as e:
        # Catch any other unexpected errors during calculation.
        # Log error with traceback info.
        logger.error(f"An unexpected error occurred during yearly metric calculation: {e}. "
                    f"Returning empty yearly metrics.", exc_info=True)
        return pd.DataFrame(columns=output_columns)  # Return empty df.

# ##### Main Execution Block (Optional) #####
# if __name__ == '__main__':
#     # Configure logging for basic output if run directly
#     logging.basicConfig(level=logging.INFO)
#
#     # Define column names for example
#     date_col_example = 'Innsamlingsdato/-tid'
#     ind_col_example = 'Antall Individer'
#
#     # Example Usage (Requires sample data loading with RENAMED columns)
#     sample_df_success = pd.DataFrame({
#         date_col_example: ['2023-01-15', '2023-05-20', '2024-02-10', 'invalid-date'],
#         ind_col_example: [5, 10, 8, 3]
#     })
#     sample_df_fail_col = pd.DataFrame({
#         date_col_example: ['2023-01-15'],
#         # ind_col_example: [5] # Missing column
#     })
#     sample_df_empty = pd.DataFrame()
#
#     print("--- Testing Success Case ---")
#     yearly_data_success = calculate_yearly_metrics(
#         sample_df_success,
#         date_col_name=date_col_example,
#         individuals_col_name=ind_col_example
#     )
#     print(yearly_data_success)
#
#     print("\n--- Testing Missing Column Case ---")
#     yearly_data_fail = calculate_yearly_metrics(
#         sample_df_fail_col,
#         date_col_name=date_col_example,
#         individuals_col_name=ind_col_example
#     )
#     print(yearly_data_fail)
#
#     print("\n--- Testing Empty Input Case ---")
#     yearly_data_empty = calculate_yearly_metrics(
#         sample_df_empty,
#         date_col_name=date_col_example,
#         individuals_col_name=ind_col_example
#     )
#     print(yearly_data_empty)
#     pass

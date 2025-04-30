\
##### Imports #####
import pandas as pd # Import pandas for data manipulation.
import logging # Import logging module.

# --- Setup Logging ---
# Get a logger instance for this module.
logger = logging.getLogger(__name__)

##### Calculation Function #####

# --- Function: calculate_yearly_metrics ---
# Calculates yearly sums of observations and individuals, and the average individuals per observation.
# Takes the DataFrame, the name of the date column, and the name of the individuals column.
# Returns an empty DataFrame if required columns are missing or other KeyErrors occur.
def calculate_yearly_metrics(data, date_col_name: str, individuals_col_name: str):
    # --- Define expected output columns for empty DataFrame case ---
    output_columns = ['Year', 'Sum_Observations', 'Sum_Individuals', 'Avg_Individuals_Per_Observation']

    # --- Initial Check (Optional but good practice) ---
    # Quick check if input is empty or not a DataFrame, return early.
    if not isinstance(data, pd.DataFrame) or data.empty:
        logger.warning("Input data is not a DataFrame or is empty. Returning empty yearly metrics.") # Log warning.
        return pd.DataFrame(columns=output_columns) # Return empty df.

    # --- Core Calculation with Error Handling ---
    try:
        # Check if required columns exist before processing using the provided names.
        if date_col_name not in data.columns:
            logger.error(f"Required date column '{date_col_name}' not found in input data. Returning empty yearly metrics.") # Log specific error.
            return pd.DataFrame(columns=output_columns) # Return empty df.
        if individuals_col_name not in data.columns:
            logger.error(f"Required individuals column '{individuals_col_name}' not found in input data. Returning empty yearly metrics.") # Log specific error.
            return pd.DataFrame(columns=output_columns) # Return empty df.

        # --- Data Preparation ---
        df = data.copy() # Create a copy.
        # Convert date column, coercing errors.
        df[date_col_name] = pd.to_datetime(df[date_col_name], errors='coerce')
        df.dropna(subset=[date_col_name], inplace=True) # Drop rows where date conversion failed.

        # Handle empty DataFrame after date conversion/dropna
        if df.empty:
             logger.warning("DataFrame became empty after date conversion/dropping NaTs. Returning empty yearly metrics.") # Log warning.
             return pd.DataFrame(columns=output_columns) # Return empty df.

        df['Year'] = df[date_col_name].dt.year # Extract year.

        # --- Aggregation ---
        # Group by year and aggregate using the provided individuals column name.
        yearly_summary = df.groupby('Year').agg(
            Sum_Observations=('Year', 'size'), # Count observations.
            Sum_Individuals=(individuals_col_name, 'sum') # Sum individuals using the provided column name.
        ).reset_index() # Reset index.

        # --- Calculate Average ---
        # Calculate average, handling potential division by zero.
        yearly_summary['Avg_Individuals_Per_Observation'] = yearly_summary['Sum_Individuals'] / yearly_summary['Sum_Observations']
        yearly_summary['Avg_Individuals_Per_Observation'].fillna(0, inplace=True) # Fill NaN with 0.

        # --- Return Result ---
        return yearly_summary # Return the calculated yearly metrics.

    except KeyError as e:
        # Catch potential KeyErrors during processing (e.g., unforeseen column issues)
        logger.error(f"A KeyError occurred during yearly metric calculation: {e}. Columns available: {list(data.columns)}. Returning empty yearly metrics.") # Log the error and available columns.
        return pd.DataFrame(columns=output_columns) # Return empty df.
    except Exception as e:
        # Catch any other unexpected errors during calculation.
        logger.error(f"An unexpected error occurred during yearly metric calculation: {e}. Returning empty yearly metrics.", exc_info=True) # Log error with traceback info.
        return pd.DataFrame(columns=output_columns) # Return empty df.

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
#     yearly_data_success = calculate_yearly_metrics(sample_df_success, date_col_name=date_col_example, individuals_col_name=ind_col_example)
#     print(yearly_data_success)
#
#     print("\n--- Testing Missing Column Case ---")
#     yearly_data_fail = calculate_yearly_metrics(sample_df_fail_col, date_col_name=date_col_example, individuals_col_name=ind_col_example)
#     print(yearly_data_fail)
#
#     print("\n--- Testing Empty Input Case ---")
#     yearly_data_empty = calculate_yearly_metrics(sample_df_empty, date_col_name=date_col_example, individuals_col_name=ind_col_example)
#     print(yearly_data_empty)
#     pass

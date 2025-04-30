\
##### Imports #####
import pytest # Import pytest for testing framework features.
import pandas as pd # Import pandas for DataFrame creation and manipulation.
from pandas.testing import assert_frame_equal # Import specific assertion for DataFrames.

# --- Module under test ---
# Use absolute import from the project source directory
from mapper_streamlit.landingsside.figures_dashboard.obs_periode_calculations import calculate_yearly_metrics # Import the function to be tested.

##### Constants #####
DATE_COL = "Innsamlingsdato/-tid" # Define renamed date column constant.
IND_COL = "Antall Individer" # Define renamed individuals column constant.
OUTPUT_COLS = ['Year', 'Sum_Observations', 'Sum_Individuals', 'Avg_Individuals_Per_Observation'] # Expected output columns.

##### Fixtures #####

# --- Fixture: basic_valid_data ---
# Provides a simple DataFrame with valid data spanning multiple years.
@pytest.fixture
def basic_valid_data():
    data = {
        DATE_COL: [
            '2022-03-15 10:00:00', '2022-07-20 11:00:00', '2023-01-10 09:30:00',
            '2023-11-05 14:15:00', '2022-04-01 12:00:00'
        ],
        IND_COL: [5, 10, 8, 12, 7]
    }
    return pd.DataFrame(data) # Return DataFrame created from the dictionary.

# --- Fixture: data_with_invalid_dates ---
# Provides data including invalid date strings and NaN/None.
@pytest.fixture
def data_with_invalid_dates():
    data = {
        DATE_COL: [
            '2022-03-15 10:00:00', 'invalid-date-string', None, '2023-01-10 09:30:00',
            '2022-13-01 00:00:00', # Invalid month
            pd.NaT, '2023-11-05 14:15:00'
        ],
        IND_COL: [5, 100, 200, 8, 300, 400, 12]
    }
    return pd.DataFrame(data) # Return DataFrame.

# --- Fixture: data_with_zero_individuals ---
# Provides data where one year has observations but zero individuals.
@pytest.fixture
def data_with_zero_individuals():
    data = {
        DATE_COL: ['2022-03-15', '2022-07-20', '2023-01-10', '2023-11-05'],
        IND_COL: [0, 0, 8, 12]
    }
    return pd.DataFrame(data) # Return DataFrame.

##### Test Cases #####

# --- Test: Happy Path --- #
def test_calculate_yearly_metrics_happy_path(basic_valid_data):
    # Arrange: Use the basic_valid_data fixture.
    expected_data = {
        'Year': [2022, 2023],
        'Sum_Observations': [3, 2],
        'Sum_Individuals': [22, 20], # 5+10+7=22, 8+12=20
        'Avg_Individuals_Per_Observation': [22/3, 10.0] # 7.333..., 10.0
    }
    expected_df = pd.DataFrame(expected_data) # Create expected result DataFrame.
    # Set Year as float to match potential output type before approx comparison
    # expected_df['Year'] = expected_df['Year'].astype(float)

    # Act: Call the function under test.
    result_df = calculate_yearly_metrics(basic_valid_data, date_col_name=DATE_COL, individuals_col_name=IND_COL)

    # Assert: Check if the result matches the expected DataFrame.
    # Use check_like=True to ignore order of rows/columns if necessary, check_dtype=False allows for float comparison variations.
    # Use pytest.approx for floating point averages.
    assert_frame_equal(result_df, expected_df, check_dtype=False, atol=0.01) # Assert equality, allowing for float tolerance.
    assert result_df['Year'].tolist() == [2022, 2023] # Explicitly check year order/values.
    assert result_df['Sum_Observations'].tolist() == [3, 2] # Check observation counts.
    assert result_df['Sum_Individuals'].tolist() == [22, 20] # Check individual sums.
    assert result_df['Avg_Individuals_Per_Observation'].tolist() == pytest.approx([22/3, 10.0], abs=0.01) # Check average with tolerance.

# --- Test: Empty Input --- #
def test_calculate_yearly_metrics_empty_input():
    # Arrange: Create an empty DataFrame.
    empty_df = pd.DataFrame(columns=[DATE_COL, IND_COL])
    expected_df = pd.DataFrame(columns=OUTPUT_COLS) # Expected output is empty df with correct columns.

    # Act: Call the function with empty data.
    result_df = calculate_yearly_metrics(empty_df, date_col_name=DATE_COL, individuals_col_name=IND_COL)

    # Assert: Check if the result is an empty DataFrame with the expected columns.
    assert_frame_equal(result_df, expected_df, check_dtype=False) # Assert equality.
    assert result_df.empty # Double check it's empty.
    assert list(result_df.columns) == OUTPUT_COLS # Verify column names and order.

# --- Test: Missing Date Column --- #
def test_calculate_yearly_metrics_missing_date_column():
    # Arrange: Create DataFrame without the date column.
    data = {IND_COL: [1, 2, 3]}
    missing_col_df = pd.DataFrame(data)
    expected_df = pd.DataFrame(columns=OUTPUT_COLS) # Expect empty DataFrame.

    # Act: Call the function.
    result_df = calculate_yearly_metrics(missing_col_df, date_col_name=DATE_COL, individuals_col_name=IND_COL)

    # Assert: Check if the result is the expected empty DataFrame.
    assert_frame_equal(result_df, expected_df, check_dtype=False) # Assert equality.

# --- Test: Missing Individuals Column --- #
def test_calculate_yearly_metrics_missing_individuals_column():
    # Arrange: Create DataFrame without the individuals column.
    data = {DATE_COL: ['2023-01-01', '2023-02-01']}
    missing_col_df = pd.DataFrame(data)
    expected_df = pd.DataFrame(columns=OUTPUT_COLS) # Expect empty DataFrame.

    # Act: Call the function.
    result_df = calculate_yearly_metrics(missing_col_df, date_col_name=DATE_COL, individuals_col_name=IND_COL)

    # Assert: Check if the result is the expected empty DataFrame.
    assert_frame_equal(result_df, expected_df, check_dtype=False) # Assert equality.

# --- Test: Invalid Dates Handling --- #
def test_calculate_yearly_metrics_invalid_dates(data_with_invalid_dates):
    # Arrange: Use the fixture with invalid dates.
    # Expected result based only on valid dates: '2022-03-15' and '2023-01-10', '2023-11-05'
    expected_data = {
        'Year': [2022, 2023],
        'Sum_Observations': [1, 2],
        'Sum_Individuals': [5, 20], # 5 from 2022, 8+12=20 from 2023
        'Avg_Individuals_Per_Observation': [5.0, 10.0] # 5/1, 20/2
    }
    expected_df = pd.DataFrame(expected_data) # Create expected DataFrame.

    # Act: Call the function.
    result_df = calculate_yearly_metrics(data_with_invalid_dates, date_col_name=DATE_COL, individuals_col_name=IND_COL)

    # Assert: Check if the result matches the expected, ignoring invalid rows.
    assert_frame_equal(result_df, expected_df, check_dtype=False) # Assert equality.

# --- Test: All Invalid Dates --- #
def test_calculate_yearly_metrics_all_invalid_dates():
    # Arrange: Create data with only invalid dates.
    data = {
        DATE_COL: ['invalid', None, pd.NaT],
        IND_COL: [1, 2, 3]
    }
    all_invalid_df = pd.DataFrame(data)
    expected_df = pd.DataFrame(columns=OUTPUT_COLS) # Expect empty output.

    # Act: Call the function.
    result_df = calculate_yearly_metrics(all_invalid_df, date_col_name=DATE_COL, individuals_col_name=IND_COL)

    # Assert: Check if the result is the expected empty DataFrame.
    assert_frame_equal(result_df, expected_df, check_dtype=False) # Assert equality.

# --- Test: Zero Individuals --- #
def test_calculate_yearly_metrics_zero_individuals(data_with_zero_individuals):
    # Arrange: Use the fixture where 2022 has zero individuals.
    expected_data = {
        'Year': [2022, 2023],
        'Sum_Observations': [2, 2],
        'Sum_Individuals': [0, 20], # 0+0=0, 8+12=20
        'Avg_Individuals_Per_Observation': [0.0, 10.0] # 0/2=0, 20/2=10
    }
    expected_df = pd.DataFrame(expected_data) # Create expected DataFrame.

    # Act: Call the function.
    result_df = calculate_yearly_metrics(data_with_zero_individuals, date_col_name=DATE_COL, individuals_col_name=IND_COL)

    # Assert: Check if the average is correctly calculated as 0.0.
    assert_frame_equal(result_df, expected_df, check_dtype=False) # Assert equality.
    assert result_df.loc[result_df['Year'] == 2022, 'Avg_Individuals_Per_Observation'].iloc[0] == 0.0 # Explicit check for 0.0 average. 
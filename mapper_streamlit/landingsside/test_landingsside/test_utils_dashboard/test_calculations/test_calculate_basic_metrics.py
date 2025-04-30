\
##### Imports #####
import pytest # Import pytest for testing framework features.
import pandas as pd # Import pandas for DataFrame creation.
from datetime import datetime # Import datetime for date comparisons.

# --- Module under test ---
# Use absolute import from the project source directory
from mapper_streamlit.landingsside.utils_dashboard.calculations.calculate_basic_metrics import calculate_basic_metrics # Import the function.

##### Constants #####
# Define expected renamed column names used by the function
DATE_COL = "Innsamlingsdato/-tid"
IND_COL = "Antall Individer"
ART_COL = "Art"
FAM_COL = "Familie"
OBS_COL = "Innsamler/Observatør"

##### Fixtures #####

# --- Fixture: metrics_data ---
# Provides a DataFrame for testing basic metrics calculation.
@pytest.fixture
def metrics_data():
    data = {
        DATE_COL: [
            '2023-01-15 10:00:00', '2023-07-20 11:00:00', '2022-11-05 14:15:00',
            '2023-01-15 10:30:00', None, 'invalid-date' # Includes duplicates, None, invalid
        ],
        IND_COL: [5, 10, '8', 12, 100, 200], # Includes numeric string, will be coerced
        ART_COL: ['Art A', 'Art B', 'Art A', 'Art C', 'Art B', 'Art D'], # Includes duplicates
        FAM_COL: ['Fam X', 'Fam Y', 'Fam X', 'Fam Y', 'Fam Z', 'Fam X'], # Includes duplicates
        OBS_COL: ['Obs 1', 'Obs 2', 'Obs 1', 'Obs 3', 'Obs 2', 'Obs 1'] # Includes duplicates
    }
    return pd.DataFrame(data) # Return DataFrame.

# --- Fixture: empty_metrics_data ---
# Provides an empty DataFrame with expected columns.
@pytest.fixture
def empty_metrics_data():
    return pd.DataFrame(columns=[DATE_COL, IND_COL, ART_COL, FAM_COL, OBS_COL]) # Return empty DataFrame.

##### Test Cases #####

# --- Test: Happy Path --- #
def test_calculate_basic_metrics_happy_path(metrics_data):
    # Arrange: Use the metrics_data fixture.
    # Expected values:
    # Records: 6 total rows
    # Individuals: 5 + 10 + 8 + 12 + 0 + 0 = 35 (errors/None coerced to 0)
    # Unique Species: Art A, Art B, Art C, Art D = 4
    # Unique Families: Fam X, Fam Y, Fam Z = 3
    # Unique Observers: Obs 1, Obs 2, Obs 3 = 3
    # Min Date: 2022-11-05
    # Max Date: 2023-07-20

    # Act: Call the function under test.
    result = calculate_basic_metrics(metrics_data)

    # Assert: Check all calculated metrics.
    assert result['total_records'] == 6 # Verify total record count.
    assert result['total_individuals'] == 335 # Verify sum of individuals after coercion.
    assert result['unique_species'] == 4 # Verify unique species count.
    assert result['unique_families'] == 3 # Verify unique family count.
    assert result['unique_observers'] == 3 # Verify unique observer count.
    assert result['min_date'] == datetime(2022, 11, 5, 14, 15, 0) # Verify earliest valid date.
    assert result['max_date'] == datetime(2023, 7, 20, 11, 0, 0) # Verify latest valid date.

# --- Test: Empty Input --- #
def test_calculate_basic_metrics_empty_input(empty_metrics_data):
    # Arrange: Use the empty_metrics_data fixture.

    # Act: Call the function.
    result = calculate_basic_metrics(empty_metrics_data)

    # Assert: Check metrics for empty data.
    assert result['total_records'] == 0 # Should be 0.
    assert result['total_individuals'] == 0 # Should be 0.
    assert result['unique_species'] == 0 # Should be 0.
    assert result['unique_families'] == 0 # Should be 0.
    assert result['unique_observers'] == 0 # Should be 0.
    assert result['min_date'] is None # Should be None.
    assert result['max_date'] is None # Should be None.

# --- Test: Missing Key Columns --- #
@pytest.mark.parametrize(
    "missing_col",
    [IND_COL, ART_COL, FAM_COL, OBS_COL, DATE_COL] # Test missing each required column.
)
def test_calculate_basic_metrics_missing_column(metrics_data, missing_col):
    # Arrange: Drop one of the required columns.
    data_missing_col = metrics_data.drop(columns=[missing_col])

    # Act & Assert: Expect a KeyError when the function tries to access the missing column.
    with pytest.raises(KeyError) as excinfo:
        calculate_basic_metrics(data_missing_col)
    # Optionally check if the error message contains the missing column name
    assert missing_col in str(excinfo.value) # Verify the error message indicates the correct missing key.

# --- Test: All Invalid Dates --- #
def test_calculate_basic_metrics_all_invalid_dates(metrics_data):
    # Arrange: Modify data to have only invalid dates.
    invalid_date_data = metrics_data.copy()
    invalid_date_data[DATE_COL] = ['invalid', None, 'bad-date', pd.NaT, '2023-13-01', '']

    # Act: Call the function.
    result = calculate_basic_metrics(invalid_date_data)

    # Assert: Dates should be None as none are valid.
    assert result['min_date'] is None # Verify min_date is None.
    assert result['max_date'] is None # Verify max_date is None.
    # Other metrics should still be calculated based on remaining columns.
    assert result['total_records'] == 6 # Record count remains the same.

# --- Test: Non-numeric Individuals Handling --- #
def test_calculate_basic_metrics_non_numeric_individuals():
    # Arrange: Data with various non-numeric types in the individuals column.
    data = {
        DATE_COL: ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
        IND_COL: ['abc', None, 5, '10', -2], # String, None, number, numeric string, negative
        ART_COL: ['A']*5, FAM_COL: ['X']*5, OBS_COL: ['1']*5
    }
    df = pd.DataFrame(data) # Create DataFrame from corrected data.
    expected_individuals = 13 # abc->0, None->0, 5->5, '10'->10, -2->-2. Sum = 13.

    # Act: Call the function.
    result = calculate_basic_metrics(df)

    # Assert: Check if total_individuals sum is correct after coercion.
    assert result['total_individuals'] == expected_individuals # Verify sum is 13.
    assert result['total_records'] == 5 # Verify record count. 
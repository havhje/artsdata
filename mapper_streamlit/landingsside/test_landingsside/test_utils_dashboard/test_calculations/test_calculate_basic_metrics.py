\
##### Imports #####
import pytest # Import pytest for testing framework features.
import pandas as pd # Import pandas for DataFrame creation.
from datetime import datetime # Import datetime for date comparisons.

# --- Module under test ---
# Use absolute import from the project source directory
from mapper_streamlit.landingsside.utils_dashboard.calculations.calculate_basic_metrics import calculate_basic_metrics # Import the function.

##### Constants for Testing #####
# Define ORIGINAL column names used for testing. These must match the keys in fixtures.
TEST_ORIGINAL_DATE_COL = "Innsamlingsdato/-tid"
TEST_ORIGINAL_IND_COL = "Antall Individer"
TEST_ORIGINAL_ART_COL = "Art"
TEST_ORIGINAL_FAM_COL = "Familie"
TEST_ORIGINAL_OBS_COL = "Innsamler/Observatør"

##### Fixtures #####

# --- Fixture: metrics_data ---
# Provides a DataFrame for testing basic metrics calculation.
@pytest.fixture
def metrics_data():
    # Use TEST_ORIGINAL_* constants for keys
    data = {
        TEST_ORIGINAL_DATE_COL: [
            '2023-01-15 10:00:00', '2023-07-20 11:00:00', '2022-11-05 14:15:00',
            '2023-01-15 10:30:00', None, 'invalid-date' # Includes duplicates, None, invalid
        ],
        TEST_ORIGINAL_IND_COL: [5, 10, '8', 12, 100, 200], # Includes numeric string, will be coerced
        TEST_ORIGINAL_ART_COL: ['Art A', 'Art B', 'Art A', 'Art C', 'Art B', 'Art D'], # Includes duplicates
        TEST_ORIGINAL_FAM_COL: ['Fam X', 'Fam Y', 'Fam X', 'Fam Y', 'Fam Z', 'Fam X'], # Includes duplicates
        TEST_ORIGINAL_OBS_COL: ['Obs 1', 'Obs 2', 'Obs 1', 'Obs 3', 'Obs 2', 'Obs 1'] # Includes duplicates
    }
    return pd.DataFrame(data)

# --- Fixture: empty_metrics_data ---
# Provides an empty DataFrame with expected original columns.
@pytest.fixture
def empty_metrics_data():
    # Use TEST_ORIGINAL_* constants for columns
    return pd.DataFrame(columns=[
        TEST_ORIGINAL_DATE_COL, 
        TEST_ORIGINAL_IND_COL, 
        TEST_ORIGINAL_ART_COL, 
        TEST_ORIGINAL_FAM_COL, 
        TEST_ORIGINAL_OBS_COL
        ])

##### Test Cases #####

# --- Test: Happy Path --- #
def test_calculate_basic_metrics_happy_path(metrics_data):
    # Arrange: Use the metrics_data fixture.
    # Expected values derived from the fixture data.

    # Act: Call the function under test, passing original column names.
    result = calculate_basic_metrics(
        metrics_data,
        individual_count_col=TEST_ORIGINAL_IND_COL,
        art_col=TEST_ORIGINAL_ART_COL,
        family_col=TEST_ORIGINAL_FAM_COL,
        observer_col=TEST_ORIGINAL_OBS_COL,
        event_date_col=TEST_ORIGINAL_DATE_COL
    )

    # Assert: Check all calculated metrics.
    assert result['total_records'] == 6
    # Individuals: 5 + 10 + 8 + 12 + 100 + 200 = 335
    assert result['total_individuals'] == 335 
    assert result['unique_species'] == 4
    assert result['unique_families'] == 3
    assert result['unique_observers'] == 3
    # Note: Updated the date parsing format check
    assert result['min_date'] == datetime(2022, 11, 5, 14, 15, 0)
    assert result['max_date'] == datetime(2023, 7, 20, 11, 0, 0)

# --- Test: Empty Input --- #
def test_calculate_basic_metrics_empty_input(empty_metrics_data):
    # Arrange: Use the empty_metrics_data fixture.

    # Act: Call the function, passing original column names.
    result = calculate_basic_metrics(
        empty_metrics_data,
        individual_count_col=TEST_ORIGINAL_IND_COL,
        art_col=TEST_ORIGINAL_ART_COL,
        family_col=TEST_ORIGINAL_FAM_COL,
        observer_col=TEST_ORIGINAL_OBS_COL,
        event_date_col=TEST_ORIGINAL_DATE_COL
    )

    # Assert: Check metrics for empty data.
    assert result['total_records'] == 0
    assert result['total_individuals'] == 0
    assert result['unique_species'] == 0
    assert result['unique_families'] == 0
    assert result['unique_observers'] == 0
    assert result['min_date'] is None
    assert result['max_date'] is None

# --- Test: Missing Key Columns --- #
@pytest.mark.parametrize(
    "missing_col",
    [
        TEST_ORIGINAL_IND_COL, 
        TEST_ORIGINAL_ART_COL, 
        TEST_ORIGINAL_FAM_COL, 
        TEST_ORIGINAL_OBS_COL, 
        TEST_ORIGINAL_DATE_COL
    ]
)
def test_calculate_basic_metrics_missing_column(metrics_data, missing_col):
    # Arrange: Drop one of the required columns.
    data_missing_col = metrics_data.drop(columns=[missing_col])

    # Act & Assert: Expect a KeyError when the function tries to access the missing column.
    with pytest.raises(KeyError) as excinfo:
        calculate_basic_metrics(
            data_missing_col,
            individual_count_col=TEST_ORIGINAL_IND_COL,
            art_col=TEST_ORIGINAL_ART_COL,
            family_col=TEST_ORIGINAL_FAM_COL,
            observer_col=TEST_ORIGINAL_OBS_COL,
            event_date_col=TEST_ORIGINAL_DATE_COL
        )
    assert missing_col in str(excinfo.value)

# --- Test: All Invalid Dates --- #
def test_calculate_basic_metrics_all_invalid_dates(metrics_data):
    # Arrange: Modify data to have only invalid dates.
    invalid_date_data = metrics_data.copy()
    invalid_date_data[TEST_ORIGINAL_DATE_COL] = ['invalid', None, 'bad-date', pd.NaT, '2023-13-01', '']

    # Act: Call the function, passing original column names.
    result = calculate_basic_metrics(
        invalid_date_data,
        individual_count_col=TEST_ORIGINAL_IND_COL,
        art_col=TEST_ORIGINAL_ART_COL,
        family_col=TEST_ORIGINAL_FAM_COL,
        observer_col=TEST_ORIGINAL_OBS_COL,
        event_date_col=TEST_ORIGINAL_DATE_COL
    )

    # Assert: Dates should be None as none are valid.
    assert result['min_date'] is None
    assert result['max_date'] is None
    assert result['total_records'] == 6

# --- Test: Non-numeric Individuals Handling --- #
def test_calculate_basic_metrics_non_numeric_individuals():
    # Arrange: Data with various non-numeric types in the individuals column.
    data = {
        TEST_ORIGINAL_DATE_COL: ['01.01.2023 00:00:00']*5, # Use format function expects
        TEST_ORIGINAL_IND_COL: ['abc', None, 5, '10', -2],
        TEST_ORIGINAL_ART_COL: ['A']*5, 
        TEST_ORIGINAL_FAM_COL: ['X']*5, 
        TEST_ORIGINAL_OBS_COL: ['1']*5
    }
    df = pd.DataFrame(data)
    expected_individuals = 13 # abc->0, None->0, 5->5, '10'->10, -2->-2. Sum = 13.

    # Act: Call the function, passing original column names.
    result = calculate_basic_metrics(
        df,
        individual_count_col=TEST_ORIGINAL_IND_COL,
        art_col=TEST_ORIGINAL_ART_COL,
        family_col=TEST_ORIGINAL_FAM_COL,
        observer_col=TEST_ORIGINAL_OBS_COL,
        event_date_col=TEST_ORIGINAL_DATE_COL
    )

    # Assert: Check if total_individuals sum is correct after coercion.
    assert result['total_individuals'] == expected_individuals
    assert result['total_records'] == 5 
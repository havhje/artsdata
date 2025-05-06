\
##### Imports #####
import pytest # Import pytest for testing framework features.
import pandas as pd # Import pandas for DataFrame creation.

# --- Module under test ---
# Use absolute import from the project source directory
from mapper_streamlit.landingsside.utils_dashboard.calculations.calculate_redlists_alien_forvaltning_stats import (
    calculate_all_status_counts,
    REDLIST_CATEGORIES, # Import constants used by the function
    ALIEN_CATEGORIES_LIST # SPECIAL_STATUS_COLS removed
)

##### Constants #####
# Define expected renamed column names used by the function
CAT_COL = "Kategori (Rødliste/Fremmedart)" # This is treated as an original column name for tests
ALIEN_FLAG_COL = "Fremmede arter kategori" # This is treated as an original column name for tests

# Define the list of original special status column names for testing purposes.
# These names must match the keys in the test data fixtures.
TEST_ORIGINAL_SPECIAL_STATUS_COLS = [
    "Prioriterte Arter", 
    "Andre Spes. Hensyn.", 
    "Ansvarsarter", 
    "Spes. Økol. Former"
]

##### Fixtures #####

# --- Fixture: status_data ---
# Provides a DataFrame for testing status counts.
@pytest.fixture
def status_data():
    data = {
        CAT_COL:          ['CR', 'EN', 'VU', 'NT', 'LC', 'SE', 'HI', 'LC', 'VU', 'NE', None, 'PH'],
        ALIEN_FLAG_COL:   ['No', 'No', 'No', 'No', 'No', 'No', 'No', 'Yes','No', 'No', 'Yes','No'],
        "Prioriterte Arter": ['No', 'Yes','No', 'No', 'Yes','No', 'No', 'No', 'Yes','No', 'No', 'No'],
        "Andre Spes. Hensyn.": ['Yes','No', 'No', 'Yes','No', 'No', 'Yes','No', 'No', 'No', 'Yes','No'],
        "Ansvarsarter":     ['No', 'No', 'Yes','No', 'No', 'No', 'No', 'No', 'No', 'Yes','No', 'No'],
        "Spes. Økol. Former":['No', 'No', 'No', 'No', 'No', 'Yes','No', 'No', 'No', 'No', 'Yes','No']
    }
    # Ensure all expected special status columns exist, using the test constant
    for col in TEST_ORIGINAL_SPECIAL_STATUS_COLS:
        if col not in data:
            data[col] = ['No'] * len(data[CAT_COL])

    return pd.DataFrame(data)

# --- Fixture: empty_status_data ---
# Provides an empty DataFrame with expected columns.
@pytest.fixture
def empty_status_data():
    cols = [CAT_COL, ALIEN_FLAG_COL] + TEST_ORIGINAL_SPECIAL_STATUS_COLS
    return pd.DataFrame(columns=cols)

##### Test Cases #####

# --- Test: Happy Path --- #
def test_calculate_all_status_counts_happy_path(status_data):
    # Arrange: Use the status_data fixture.
    # Act: Call the function with required original column name parameters.
    result = calculate_all_status_counts(
        status_data, 
        category_col=CAT_COL, 
        alien_flag_col=ALIEN_FLAG_COL, 
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
    )

    # Assert: Check Red List counts.
    assert result['redlist_total'] == 5
    assert result['redlist_breakdown'] == {'CR': 1, 'EN': 1, 'VU': 2, 'NT': 1, 'DD': 0}

    # Assert: Check Alien counts.
    assert result['alien_total'] == 5
    assert result['alien_breakdown'] == {'SE': 1, 'HI': 1, 'PH': 1, 'LO': 0}

    # Assert: Check Special Status counts.
    # The keys in special_status_breakdown will be the original names from TEST_ORIGINAL_SPECIAL_STATUS_COLS
    assert result['special_status_total'] == 11 
    assert result['special_status_breakdown'] == {
        "Prioriterte Arter": 3,
        "Andre Spes. Hensyn.": 4, # Updated expected count based on fixture data
        "Ansvarsarter": 2,
        "Spes. Økol. Former": 2
    }

    # Assert: Check returned order lists match constants.
    assert result['redlist_categories_order'] == REDLIST_CATEGORIES
    assert result['alien_categories_order'] == ALIEN_CATEGORIES_LIST
    assert result['special_status_cols_order'] == TEST_ORIGINAL_SPECIAL_STATUS_COLS # Check against local test constant

# --- Test: Empty Input --- #
def test_calculate_all_status_counts_empty_input(empty_status_data):
    # Act: Call the function.
    result = calculate_all_status_counts(
        empty_status_data, 
        category_col=CAT_COL, 
        alien_flag_col=ALIEN_FLAG_COL, 
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
    )

    # Assert: All counts should be zero.
    assert result['redlist_total'] == 0
    assert result['redlist_breakdown'] == {'CR': 0, 'EN': 0, 'VU': 0, 'NT': 0, 'DD': 0}
    assert result['alien_total'] == 0
    assert result['alien_breakdown'] == {'SE': 0, 'HI': 0, 'PH': 0, 'LO': 0}
    assert result['special_status_total'] == 0
    # Expect keys to be from TEST_ORIGINAL_SPECIAL_STATUS_COLS with 0 counts
    expected_special_breakdown = {col: 0 for col in TEST_ORIGINAL_SPECIAL_STATUS_COLS}
    assert result['special_status_breakdown'] == expected_special_breakdown

# --- Test: Missing Key Columns (CAT_COL and ALIEN_FLAG_COL only) --- #
@pytest.mark.parametrize(
    "missing_col",
    [CAT_COL, ALIEN_FLAG_COL] # Only these will now cause a KeyError with current function implementation
)
def test_calculate_all_status_counts_missing_critical_column(status_data, missing_col):
    # Arrange: Drop one of the critical columns (CAT_COL or ALIEN_FLAG_COL).
    data_missing_col = status_data.drop(columns=[missing_col])

    # Act & Assert: Expect a KeyError when the function tries to access these specific missing columns.
    with pytest.raises(KeyError) as excinfo:
        calculate_all_status_counts(
            data_missing_col, 
            category_col=CAT_COL, 
            alien_flag_col=ALIEN_FLAG_COL, 
            original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
        )
    assert missing_col in str(excinfo.value)

# --- Test: Missing Optional Special Status Column (should not raise KeyError) --- #
def test_calculate_all_status_counts_missing_optional_special_status_col(status_data):
    # Arrange: Drop one of the special status columns from the DataFrame.
    # The function should still run and count the missing column as 0 for its breakdown.
    col_to_drop = TEST_ORIGINAL_SPECIAL_STATUS_COLS[0] # e.g., "Prioriterte Arter"
    data_missing_optional_col = status_data.drop(columns=[col_to_drop])

    # Act
    result = calculate_all_status_counts(
        data_missing_optional_col,
        category_col=CAT_COL,
        alien_flag_col=ALIEN_FLAG_COL,
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS # Pass the full list, function handles if one is not in DF
    )

    # Assert: Check that the specific dropped column count is 0, others are as expected.
    # The total special status count will be lower.
    assert result['special_status_breakdown'][col_to_drop] == 0
    # Example: check another column to ensure it's still counted correctly
    if len(TEST_ORIGINAL_SPECIAL_STATUS_COLS) > 1:
         other_col = TEST_ORIGINAL_SPECIAL_STATUS_COLS[1]
         original_fixture_count_other_col = (status_data[other_col].astype(str).str.upper() == 'YES').sum()
         assert result['special_status_breakdown'][other_col] == original_fixture_count_other_col
    # Total count will be reduced by the count of the dropped column
    original_total_special = 11 # from happy path
    original_dropped_col_count = (status_data[col_to_drop].astype(str).str.upper() == 'YES').sum()
    assert result['special_status_total'] == original_total_special - original_dropped_col_count

# --- Test: No Matches --- #
def test_calculate_all_status_counts_no_matches():
    # Arrange: Create data with no relevant status matches.
    data = {
        CAT_COL: ['LC', 'LC', 'NE', None],
        ALIEN_FLAG_COL: ['No', 'No', 'No', 'No']
    }
    for col in TEST_ORIGINAL_SPECIAL_STATUS_COLS: # Use local constant
        data[col] = ['No']*4
    no_match_df = pd.DataFrame(data)

    # Act: Call the function.
    result = calculate_all_status_counts(
        no_match_df, 
        category_col=CAT_COL, 
        alien_flag_col=ALIEN_FLAG_COL, 
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
    )

    # Assert: All counts should be zero.
    assert result['redlist_total'] == 0
    assert result['alien_total'] == 0
    assert result['special_status_total'] == 0
    assert not any(result['redlist_breakdown'].values())
    assert not any(result['alien_breakdown'].values())
    assert not any(result['special_status_breakdown'].values())

# --- Test: Alien Only via Category --- #
def test_calculate_all_status_counts_alien_only_category():
    data = {CAT_COL: ['SE', 'HI', 'LC'], ALIEN_FLAG_COL: ['No', 'No', 'No']}
    for col in TEST_ORIGINAL_SPECIAL_STATUS_COLS: data[col] = ['No'] * 3
    df = pd.DataFrame(data)
    result = calculate_all_status_counts(
        df, 
        category_col=CAT_COL, 
        alien_flag_col=ALIEN_FLAG_COL, 
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
    )
    assert result['alien_total'] == 2
    assert result['alien_breakdown'] == {'SE': 1, 'HI': 1, 'PH': 0, 'LO': 0}

# --- Test: Alien Only via Flag --- #
def test_calculate_all_status_counts_alien_only_flag():
    data = {CAT_COL: ['LC', 'LC', 'CR'], ALIEN_FLAG_COL: ['Yes', 'Yes', 'No']}
    for col in TEST_ORIGINAL_SPECIAL_STATUS_COLS: data[col] = ['No'] * 3
    df = pd.DataFrame(data)
    result = calculate_all_status_counts(
        df, 
        category_col=CAT_COL, 
        alien_flag_col=ALIEN_FLAG_COL, 
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
    )
    assert result['alien_total'] == 2
    assert result['alien_breakdown'] == {'SE': 0, 'HI': 0, 'PH': 0, 'LO': 0}

# --- Test: Alien via Both Criteria --- #
def test_calculate_all_status_counts_alien_both_criteria():
    data = {CAT_COL: ['SE', 'HI', 'LC'], ALIEN_FLAG_COL: ['Yes', 'No', 'Yes']}
    for col in TEST_ORIGINAL_SPECIAL_STATUS_COLS: data[col] = ['No'] * 3
    df = pd.DataFrame(data)
    result = calculate_all_status_counts(
        df, 
        category_col=CAT_COL, 
        alien_flag_col=ALIEN_FLAG_COL, 
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
    )
    assert result['alien_total'] == 3
    assert result['alien_breakdown'] == {'SE': 1, 'HI': 1, 'PH': 0, 'LO': 0} 
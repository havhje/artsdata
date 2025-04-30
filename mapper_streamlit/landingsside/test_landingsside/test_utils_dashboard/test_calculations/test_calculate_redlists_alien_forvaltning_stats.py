\
##### Imports #####
import pytest # Import pytest for testing framework features.
import pandas as pd # Import pandas for DataFrame creation.

# --- Module under test ---
# Use absolute import from the project source directory
from mapper_streamlit.landingsside.utils_dashboard.calculations.calculate_redlists_alien_forvaltning_stats import (
    calculate_all_status_counts,
    REDLIST_CATEGORIES, # Import constants used by the function
    ALIEN_CATEGORIES_LIST,
    SPECIAL_STATUS_COLS
)

##### Constants #####
# Define expected renamed column names used by the function
CAT_COL = "Kategori (Rødliste/Fremmedart)"
ALIEN_FLAG_COL = "Fremmede arter kategori" # Note: The function uses this specific name
# Special status columns are already imported (SPECIAL_STATUS_COLS)

##### Fixtures #####

# --- Fixture: status_data ---
# Provides a DataFrame for testing status counts.
@pytest.fixture
def status_data():
    data = {
        CAT_COL:          ['CR', 'EN', 'VU', 'NT', 'LC', 'SE', 'HI', 'LC', 'VU', 'NE', None, 'PH'],
        ALIEN_FLAG_COL:   ['No', 'No', 'No', 'No', 'No', 'No', 'No', 'Yes','No', 'No', 'Yes','No'], # Alien marked by 'Yes' flag
        "Prioriterte Arter": ['No', 'Yes','No', 'No', 'Yes','No', 'No', 'No', 'Yes','No', 'No', 'No'],
        "Andre Spes. Hensyn.": ['Yes','No', 'No', 'Yes','No', 'No', 'Yes','No', 'No', 'No', 'Yes','No'],
        "Ansvarsarter":     ['No', 'No', 'Yes','No', 'No', 'No', 'No', 'No', 'No', 'Yes','No', 'No'],
        "Spes. Økol. Former":['No', 'No', 'No', 'No', 'No', 'Yes','No', 'No', 'No', 'No', 'Yes','No']
    }
    # Ensure all expected special status columns exist, even if not in the main dict
    for col in SPECIAL_STATUS_COLS:
        if col not in data:
            data[col] = ['No'] * len(data[CAT_COL]) # Add column with 'No' if missing

    return pd.DataFrame(data) # Return DataFrame.

# --- Fixture: empty_status_data ---
# Provides an empty DataFrame with expected columns.
@pytest.fixture
def empty_status_data():
    cols = [CAT_COL, ALIEN_FLAG_COL] + SPECIAL_STATUS_COLS
    return pd.DataFrame(columns=cols) # Return empty DataFrame.

##### Test Cases #####

# --- Test: Happy Path --- #
def test_calculate_all_status_counts_happy_path(status_data):
    # Arrange: Use the status_data fixture.
    # Expected counts based on fixture:
    # Redlisted: CR(1), EN(1), VU(2), NT(1), DD(0) -> Total 5
    # Alien: SE(1), HI(1), PH(1), LO(0) from CAT_COL; Plus rows where ALIEN_FLAG_COL is 'Yes' (2 rows, indices 7 and 10)
    # Total Alien: (SE or HI or PH or LO) | (ALIEN_FLAG_COL == 'Yes') -> Indices: 5, 6, 11 (Category) | 7, 10 (Flag) -> Unique indices: 5, 6, 7, 10, 11 -> Total 5
    # Special: Prioriterte(3), Andre(3), Ansvars(2), Spes(2) -> Total 10

    # Act: Call the function.
    result = calculate_all_status_counts(status_data)

    # Assert: Check Red List counts.
    assert result['redlist_total'] == 5 # Verify total redlisted.
    assert result['redlist_breakdown'] == {'CR': 1, 'EN': 1, 'VU': 2, 'NT': 1, 'DD': 0} # Verify breakdown.

    # Assert: Check Alien counts.
    assert result['alien_total'] == 5 # Verify total alien count (unique rows).
    assert result['alien_breakdown'] == {'SE': 1, 'HI': 1, 'PH': 1, 'LO': 0} # Breakdown by category code.

    # Assert: Check Special Status counts.
    assert result['special_status_total'] == 11 # Verify total special status 'Yes'.
    assert result['special_status_breakdown'] == {
        "Prioriterte Arter": 3,
        "Andre Spes. Hensyn.": 4,
        "Ansvarsarter": 2,
        "Spes. Økol. Former": 2
    } # Verify breakdown.

    # Assert: Check returned order lists match constants.
    assert result['redlist_categories_order'] == REDLIST_CATEGORIES # Verify redlist order.
    assert result['alien_categories_order'] == ALIEN_CATEGORIES_LIST # Verify alien order.
    assert result['special_status_cols_order'] == SPECIAL_STATUS_COLS # Verify special status order.

# --- Test: Empty Input --- #
def test_calculate_all_status_counts_empty_input(empty_status_data):
    # Arrange: Use the empty_status_data fixture.

    # Act: Call the function.
    result = calculate_all_status_counts(empty_status_data)

    # Assert: All counts should be zero.
    assert result['redlist_total'] == 0
    assert result['redlist_breakdown'] == {'CR': 0, 'EN': 0, 'VU': 0, 'NT': 0, 'DD': 0}
    assert result['alien_total'] == 0
    assert result['alien_breakdown'] == {'SE': 0, 'HI': 0, 'PH': 0, 'LO': 0}
    assert result['special_status_total'] == 0
    assert result['special_status_breakdown'] == {
        "Prioriterte Arter": 0, "Andre Spes. Hensyn.": 0,
        "Ansvarsarter": 0, "Spes. Økol. Former": 0
    }

# --- Test: Missing Key Columns --- #
@pytest.mark.parametrize(
    "missing_col",
    [CAT_COL, ALIEN_FLAG_COL] + SPECIAL_STATUS_COLS # Test missing each crucial column.
)
def test_calculate_all_status_counts_missing_column(status_data, missing_col):
    # Arrange: Drop one of the required columns.
    data_missing_col = status_data.drop(columns=[missing_col])

    # Act & Assert: Expect a KeyError when the function tries to access the missing column.
    with pytest.raises(KeyError) as excinfo:
        calculate_all_status_counts(data_missing_col)
    assert missing_col in str(excinfo.value) # Verify the error indicates the correct missing key.

# --- Test: No Matches --- #
def test_calculate_all_status_counts_no_matches():
    # Arrange: Create data with no relevant status matches.
    data = {
        CAT_COL: ['LC', 'LC', 'NE', None],
        ALIEN_FLAG_COL: ['No', 'No', 'No', 'No'],
        "Prioriterte Arter": ['No']*4,
        "Andre Spes. Hensyn.": ['No']*4,
        "Ansvarsarter": ['No']*4,
        "Spes. Økol. Former": ['No']*4
    }
    no_match_df = pd.DataFrame(data)

    # Act: Call the function.
    result = calculate_all_status_counts(no_match_df)

    # Assert: All counts should be zero.
    assert result['redlist_total'] == 0
    assert result['alien_total'] == 0
    assert result['special_status_total'] == 0
    assert not any(result['redlist_breakdown'].values()) # Check all breakdown values are 0.
    assert not any(result['alien_breakdown'].values()) # Check all breakdown values are 0.
    assert not any(result['special_status_breakdown'].values()) # Check all breakdown values are 0.

# --- Test: Alien Only via Category --- #
def test_calculate_all_status_counts_alien_only_category():
    # Arrange: Data where alien status comes only from category column.
    data = {CAT_COL: ['SE', 'HI', 'LC'], ALIEN_FLAG_COL: ['No', 'No', 'No']}
     # Add required special status cols filled with 'No'
    for col in SPECIAL_STATUS_COLS: data[col] = ['No'] * 3
    df = pd.DataFrame(data)

    # Act
    result = calculate_all_status_counts(df)

    # Assert
    assert result['alien_total'] == 2 # SE and HI should count.
    assert result['alien_breakdown'] == {'SE': 1, 'HI': 1, 'PH': 0, 'LO': 0}

# --- Test: Alien Only via Flag --- #
def test_calculate_all_status_counts_alien_only_flag():
    # Arrange: Data where alien status comes only from flag column.
    data = {CAT_COL: ['LC', 'LC', 'CR'], ALIEN_FLAG_COL: ['Yes', 'Yes', 'No']}
    # Add required special status cols filled with 'No'
    for col in SPECIAL_STATUS_COLS: data[col] = ['No'] * 3
    df = pd.DataFrame(data)

    # Act
    result = calculate_all_status_counts(df)

    # Assert
    assert result['alien_total'] == 2 # Rows with 'Yes' should count.
    assert result['alien_breakdown'] == {'SE': 0, 'HI': 0, 'PH': 0, 'LO': 0} # Category breakdown is 0.

# --- Test: Alien via Both Criteria --- #
def test_calculate_all_status_counts_alien_both_criteria():
    # Arrange: Data where alien status matches both category and flag.
    data = {CAT_COL: ['SE', 'HI', 'LC'], ALIEN_FLAG_COL: ['Yes', 'No', 'Yes']}
     # Add required special status cols filled with 'No'
    for col in SPECIAL_STATUS_COLS: data[col] = ['No'] * 3
    df = pd.DataFrame(data)

    # Act
    result = calculate_all_status_counts(df)

    # Assert
    # Row 0: SE and Yes; Row 1: HI; Row 2: Yes -> Total 3 unique rows
    assert result['alien_total'] == 3
    assert result['alien_breakdown'] == {'SE': 1, 'HI': 1, 'PH': 0, 'LO': 0} # Breakdown by category. 
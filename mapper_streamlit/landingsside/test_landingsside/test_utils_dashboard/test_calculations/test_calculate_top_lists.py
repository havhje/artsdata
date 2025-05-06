\
##### Imports #####
import pytest # Import pytest for testing framework features.
import pandas as pd # Import pandas for DataFrame creation and manipulation.
from pandas.testing import assert_frame_equal # Import specific assertion for DataFrames.

# --- Module under test ---
# Use absolute import from the project source directory
from mapper_streamlit.landingsside.utils_dashboard.calculations.calculate_top_lists import (
    calculate_all_top_lists,
    _prepare_data_for_top_lists, # Import helper function as well
    # Constants like REDLIST_CATEGORIES, ALIEN_CATEGORIES_LIST are needed by the function but not directly by tests
    # SPECIAL_STATUS_COLS and CATEGORY_COL removed
)

##### Constants for Testing #####
# Define expected ORIGINAL column names used by the function being tested
# These must match the keys/columns used in the test fixtures.
TEST_ORIGINAL_ART_COL = "Art"
TEST_ORIGINAL_FAM_COL = "Familie"
TEST_ORIGINAL_OBS_COL = "Innsamler/Observatør"
TEST_ORIGINAL_IND_COL = "Antall Individer"
TEST_ORIGINAL_CATEGORY_COL = "Kategori (Rødliste/Fremmedart)"
TEST_ORIGINAL_SPECIAL_STATUS_COLS = [
    "Prioriterte Arter", 
    "Andre Spes. Hensyn.", 
    "Ansvarsarter", 
    "Spes. Økol. Former"
]

# Column added by helper function - internal processing detail
NUM_IND_COL = "Antall Individer Num"

##### Fixtures #####

# --- Fixture: top_list_data ---
# Provides a DataFrame for testing top list calculations.
@pytest.fixture
def top_list_data():
    # Use the TEST_ORIGINAL_* constants for keys
    data = {
        TEST_ORIGINAL_ART_COL:      ['Art A', 'Art B', 'Art A', 'Art C', 'Art B', 'Art A', 'Art D', 'Art E', 'Art F', 'Art G'],
        TEST_ORIGINAL_FAM_COL:      ['Fam X', 'Fam Y', 'Fam X', 'Fam Y', 'Fam Y', 'Fam X', 'Fam Z', 'Fam Z', 'Fam A', 'Fam A'],
        TEST_ORIGINAL_OBS_COL:      ['Obs 1', 'Obs 2', 'Obs 1', 'Obs 3', 'Obs 2', 'Obs 2', 'Obs 4', 'Obs 1', 'Obs 5', 'Obs 5'],
        TEST_ORIGINAL_IND_COL:      [5,       10,      8,       '12',    1,       15,      'abc',   20,      2,       3], # Mix of types
        TEST_ORIGINAL_CATEGORY_COL: ['CR',    'EN',    'CR',    'SE',    'HI',    'CR',    'LC',    'VU',    'SE',    'NT'],
        # Use original names directly as keys, matching TEST_ORIGINAL_SPECIAL_STATUS_COLS
        "Prioriterte Arter":['Yes',   'No',    'Yes',   'No',    'No',    'No',    'Yes',   'Yes',   'No',    'No'],
        "Andre Spes. Hensyn.": ['No']*10,
        "Ansvarsarter":      ['No', 'Yes', 'No', 'Yes', 'No', 'No', 'No', 'No', 'No', 'Yes'],
        "Spes. Økol. Former":['No']*10,
    }
    return pd.DataFrame(data)

# --- Fixture: empty_top_list_data ---
# Provides an empty DataFrame with expected original columns.
@pytest.fixture
def empty_top_list_data():
    # Define columns using the original names defined in test constants
    cols = [
        TEST_ORIGINAL_ART_COL, 
        TEST_ORIGINAL_FAM_COL, 
        TEST_ORIGINAL_OBS_COL, 
        TEST_ORIGINAL_IND_COL, 
        TEST_ORIGINAL_CATEGORY_COL
        ] + TEST_ORIGINAL_SPECIAL_STATUS_COLS
    return pd.DataFrame(columns=cols)

##### Test Cases: _prepare_data_for_top_lists #####

def test_prepare_data_adds_numeric_column(top_list_data):
    # Arrange: Use original ind col constant
    df = top_list_data
    original_ind_col = TEST_ORIGINAL_IND_COL 
    # Act: Pass the original column name
    prepared_df = _prepare_data_for_top_lists(df, original_individual_count_col=original_ind_col)
    # Assert
    assert NUM_IND_COL in prepared_df.columns 
    assert pd.api.types.is_numeric_dtype(prepared_df[NUM_IND_COL]) 
    expected_numeric = [5.0, 10.0, 8.0, 12.0, 1.0, 15.0, 0.0, 20.0, 2.0, 3.0]
    assert prepared_df[NUM_IND_COL].tolist() == expected_numeric

def test_prepare_data_does_not_modify_original(top_list_data):
    # Arrange
    df_original = top_list_data
    original_ind_col = TEST_ORIGINAL_IND_COL
    df_copy_before = df_original.copy()
    # Act
    _ = _prepare_data_for_top_lists(df_original, original_individual_count_col=original_ind_col)
    # Assert
    assert_frame_equal(df_original, df_copy_before)
    assert NUM_IND_COL not in df_original.columns

##### Test Cases: calculate_all_top_lists #####

# --- Test: Happy Path (top_n = 3) --- #
def test_calculate_all_top_lists_happy_path(top_list_data):
    # Arrange
    top_n = 3

    # Act: Pass all required original column names
    result = calculate_all_top_lists(
        top_list_data, 
        top_n=top_n,
        art_col=TEST_ORIGINAL_ART_COL,
        family_col=TEST_ORIGINAL_FAM_COL,
        observer_col=TEST_ORIGINAL_OBS_COL,
        individual_count_col=TEST_ORIGINAL_IND_COL,
        category_col=TEST_ORIGINAL_CATEGORY_COL,
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
        )

    # Assert: Check structure
    assert isinstance(result, dict)
    expected_keys = [
        "top_species_freq", "top_families_freq", "top_observers_freq",
        "top_individual_obs", "top_redlist_species_agg",
        "top_alien_species_agg", "top_special_species_agg"
    ]
    assert all(key in result for key in expected_keys)

    # Assert: Top Species Freq (Art A:3, Art B:2, Art C:1 / Art D:1 / ...)
    top_species = result["top_species_freq"]
    assert len(top_species) == top_n
    assert top_species[TEST_ORIGINAL_ART_COL].tolist() == ['Art A', 'Art B', 'Art C'] # Check species order using original col
    assert top_species['Antall_Observasjoner'].tolist() == [3, 2, 1]

    # Assert: Top Families Freq (Fam X:3, Fam Y:3, Fam Z:2)
    top_families = result["top_families_freq"]
    assert len(top_families) == top_n
    assert sorted(top_families[TEST_ORIGINAL_FAM_COL].tolist()) == sorted(['Fam X', 'Fam Y', 'Fam Z']) # Use original col
    assert sorted(top_families['Antall_Observasjoner'].tolist(), reverse=True) == [3, 3, 2]

    # Assert: Top Observers Freq (Obs 1:3, Obs 2:3, Obs 5:2)
    top_observers = result["top_observers_freq"]
    assert len(top_observers) == top_n
    assert sorted(top_observers[TEST_ORIGINAL_OBS_COL].tolist()) == sorted(['Obs 1', 'Obs 2', 'Obs 5']) # Use original col
    assert sorted(top_observers['Antall_Observasjoner'].tolist(), reverse=True) == [3, 3, 2]

    # Assert: Top Individual Obs (Indices: 7(20), 5(15), 3(12))
    top_inds = result["top_individual_obs"]
    assert len(top_inds) == top_n
    assert top_inds.index.tolist() == [7, 5, 3]
    assert top_inds[NUM_IND_COL].tolist() == [20.0, 15.0, 12.0]
    assert TEST_ORIGINAL_ART_COL in top_inds.columns # Check original art col is present

    # Assert: Aggregated Lists (Example: Redlist CR)
    cr_agg = result["top_redlist_species_agg"]['CR']
    assert len(cr_agg) == 1 
    assert cr_agg.iloc[0][TEST_ORIGINAL_ART_COL] == 'Art A' # Use original col
    assert cr_agg.iloc[0]['Antall_Observasjoner'] == 3
    assert cr_agg.iloc[0]['Sum_Individer'] == 28

    # Assert: Aggregated Lists (Example: Alien SE)
    se_agg = result["top_alien_species_agg"]['SE']
    assert len(se_agg) == 2
    se_agg = se_agg.sort_values(by=TEST_ORIGINAL_ART_COL).reset_index() # Use original col for sort
    assert se_agg.loc[0, TEST_ORIGINAL_ART_COL] == 'Art C' and se_agg.loc[0, 'Antall_Observasjoner'] == 1 and se_agg.loc[0, 'Sum_Individer'] == 12
    assert se_agg.loc[1, TEST_ORIGINAL_ART_COL] == 'Art F' and se_agg.loc[1, 'Antall_Observasjoner'] == 1 and se_agg.loc[1, 'Sum_Individer'] == 2

    # Assert: Aggregated Lists (Example: Prioriterte Arter)
    # The key for the aggregated dict is now the original column name
    prio_agg = result["top_special_species_agg"]["Prioriterte Arter"]
    assert len(prio_agg) == 3
    # Check species using original column name
    assert prio_agg.iloc[0][TEST_ORIGINAL_ART_COL] == 'Art A' and prio_agg.iloc[0]['Antall_Observasjoner'] == 2 and prio_agg.iloc[0]['Sum_Individer'] == 13
    assert prio_agg.iloc[1][TEST_ORIGINAL_ART_COL] == 'Art E' and prio_agg.iloc[1]['Antall_Observasjoner'] == 1 and prio_agg.iloc[1]['Sum_Individer'] == 20
    assert prio_agg.iloc[2][TEST_ORIGINAL_ART_COL] == 'Art D' and prio_agg.iloc[2]['Antall_Observasjoner'] == 1 and prio_agg.iloc[2]['Sum_Individer'] == 0

# --- Test: Empty Input --- #
def test_calculate_all_top_lists_empty_input(empty_top_list_data):
    # Act: Pass original column names
    result = calculate_all_top_lists(
        empty_top_list_data, 
        top_n=5,
        art_col=TEST_ORIGINAL_ART_COL,
        family_col=TEST_ORIGINAL_FAM_COL,
        observer_col=TEST_ORIGINAL_OBS_COL,
        individual_count_col=TEST_ORIGINAL_IND_COL,
        category_col=TEST_ORIGINAL_CATEGORY_COL,
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
    )
    # Assert: Check main list types and emptiness
    assert isinstance(result["top_species_freq"], pd.DataFrame) and result["top_species_freq"].empty
    assert isinstance(result["top_families_freq"], pd.DataFrame) and result["top_families_freq"].empty
    assert isinstance(result["top_observers_freq"], pd.DataFrame) and result["top_observers_freq"].empty
    assert isinstance(result["top_individual_obs"], pd.DataFrame) and result["top_individual_obs"].empty
    # Assert: Check aggregated dicts are present and contain empty DataFrames
    assert isinstance(result["top_redlist_species_agg"], dict)
    assert all(isinstance(df, pd.DataFrame) and df.empty for df in result["top_redlist_species_agg"].values())
    assert isinstance(result["top_alien_species_agg"], dict)
    assert all(isinstance(df, pd.DataFrame) and df.empty for df in result["top_alien_species_agg"].values())
    assert isinstance(result["top_special_species_agg"], dict)
    assert all(isinstance(df, pd.DataFrame) and df.empty for df in result["top_special_species_agg"].values())

# --- Test: Fewer items than top_n --- #
def test_calculate_all_top_lists_fewer_items_than_top_n(top_list_data):
    # Arrange
    top_n = 10
    # Act: Pass original column names
    result = calculate_all_top_lists(
        top_list_data, 
        top_n=top_n,
        art_col=TEST_ORIGINAL_ART_COL,
        family_col=TEST_ORIGINAL_FAM_COL,
        observer_col=TEST_ORIGINAL_OBS_COL,
        individual_count_col=TEST_ORIGINAL_IND_COL,
        category_col=TEST_ORIGINAL_CATEGORY_COL,
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
    )
    # Assert
    assert len(result["top_species_freq"]) == 7 
    assert len(result["top_families_freq"]) == 4 
    assert len(result["top_observers_freq"]) == 5 
    assert len(result["top_individual_obs"]) == min(top_n, len(top_list_data))

# --- Test: Missing Critical Column --- #
@pytest.mark.parametrize(
    "missing_col",
    [
        TEST_ORIGINAL_ART_COL,
        TEST_ORIGINAL_FAM_COL,
        TEST_ORIGINAL_OBS_COL,
        TEST_ORIGINAL_IND_COL,
        TEST_ORIGINAL_CATEGORY_COL,
    ] # Only test critical columns that function relies on directly
)
def test_calculate_all_top_lists_missing_critical_column(top_list_data, missing_col):
    # Arrange: Drop a critical column.
    data_missing_col = top_list_data.drop(columns=[missing_col])
    # Act & Assert: Expect KeyError when calculating list requiring the missing column.
    with pytest.raises(KeyError) as excinfo:
        calculate_all_top_lists(
            data_missing_col, 
            top_n=3,
            art_col=TEST_ORIGINAL_ART_COL,
            family_col=TEST_ORIGINAL_FAM_COL,
            observer_col=TEST_ORIGINAL_OBS_COL,
            individual_count_col=TEST_ORIGINAL_IND_COL,
            category_col=TEST_ORIGINAL_CATEGORY_COL,
            original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
        )
    assert missing_col in str(excinfo.value) # Verify the error message.

# --- Test: No Data for Specific Category --- #
def test_calculate_all_top_lists_no_data_for_category(top_list_data):
    # Arrange: Use standard data, check a category with no entries (e.g., DD).
    # Act: Pass original column names
    result = calculate_all_top_lists(
        top_list_data, 
        top_n=3,
        art_col=TEST_ORIGINAL_ART_COL,
        family_col=TEST_ORIGINAL_FAM_COL,
        observer_col=TEST_ORIGINAL_OBS_COL,
        individual_count_col=TEST_ORIGINAL_IND_COL,
        category_col=TEST_ORIGINAL_CATEGORY_COL,
        original_special_status_cols=TEST_ORIGINAL_SPECIAL_STATUS_COLS
    )
    # Assert
    assert 'DD' in result["top_redlist_species_agg"]
    dd_agg = result["top_redlist_species_agg"]['DD']
    assert isinstance(dd_agg, pd.DataFrame)
    assert dd_agg.empty
    # Check columns are the original Art column and the generic aggregate names
    assert list(dd_agg.columns) == [TEST_ORIGINAL_ART_COL, 'Antall_Observasjoner', 'Sum_Individer'] 
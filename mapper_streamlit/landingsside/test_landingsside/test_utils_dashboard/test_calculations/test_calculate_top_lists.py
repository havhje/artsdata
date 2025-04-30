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
    # Import constants used by the function (might be needed for expected dict keys)
    # REDLIST_CATEGORIES, # Not explicitly used in tests, only needed for function internals
    # ALIEN_CATEGORIES_LIST, # Not explicitly used in tests
    SPECIAL_STATUS_COLS,
    CATEGORY_COL
)

##### Constants #####
# Define expected renamed column names used by the function
ART_COL = "Art"
FAM_COL = "Familie"
OBS_COL = "Innsamler/Observatør"
IND_COL = "Antall Individer"
# CATEGORY_COL and SPECIAL_STATUS_COLS are imported
NUM_IND_COL = "Antall Individer Num" # Column added by helper

##### Fixtures #####

# --- Fixture: top_list_data ---
# Provides a DataFrame for testing top list calculations.
@pytest.fixture
def top_list_data():
    data = {
        ART_COL:          ['Art A', 'Art B', 'Art A', 'Art C', 'Art B', 'Art A', 'Art D', 'Art E', 'Art F', 'Art G'],
        FAM_COL:          ['Fam X', 'Fam Y', 'Fam X', 'Fam Y', 'Fam Y', 'Fam X', 'Fam Z', 'Fam Z', 'Fam A', 'Fam A'],
        OBS_COL:          ['Obs 1', 'Obs 2', 'Obs 1', 'Obs 3', 'Obs 2', 'Obs 2', 'Obs 4', 'Obs 1', 'Obs 5', 'Obs 5'],
        IND_COL:          [5,       10,      8,       '12',    1,       15,      'abc',   20,      2,       3], # Mix of types
        CATEGORY_COL:     ['CR',    'EN',    'CR',    'SE',    'HI',    'CR',    'LC',    'VU',    'SE',    'NT'],
        "Prioriterte Arter":['Yes',   'No',    'Yes',   'No',    'No',    'No',    'Yes',   'Yes',   'No',    'No'],
        # Add other special status columns, simplifying for test clarity
        "Andre Spes. Hensyn.": ['No']*10,
        "Ansvarsarter":      ['No', 'Yes', 'No', 'Yes', 'No', 'No', 'No', 'No', 'No', 'Yes'],
        "Spes. Økol. Former":['No']*10,
    }
    return pd.DataFrame(data) # Return DataFrame.

# --- Fixture: empty_top_list_data ---
# Provides an empty DataFrame with expected columns.
@pytest.fixture
def empty_top_list_data():
    cols = [ART_COL, FAM_COL, OBS_COL, IND_COL, CATEGORY_COL] + SPECIAL_STATUS_COLS
    return pd.DataFrame(columns=cols) # Return empty DataFrame.

##### Test Cases: _prepare_data_for_top_lists #####

def test_prepare_data_adds_numeric_column(top_list_data):
    # Arrange
    df = top_list_data
    # Act
    prepared_df = _prepare_data_for_top_lists(df)
    # Assert
    assert NUM_IND_COL in prepared_df.columns # Check column added.
    assert pd.api.types.is_numeric_dtype(prepared_df[NUM_IND_COL]) # Check dtype is numeric.
    # Check specific conversions: 5, 10, 8, 12, 1, 15, 0 (abc), 20, 2, 3
    expected_numeric = [5.0, 10.0, 8.0, 12.0, 1.0, 15.0, 0.0, 20.0, 2.0, 3.0]
    assert prepared_df[NUM_IND_COL].tolist() == expected_numeric # Verify values.

def test_prepare_data_does_not_modify_original(top_list_data):
    # Arrange
    df_original = top_list_data
    df_copy_before = df_original.copy() # Make a copy for comparison
    # Act
    _ = _prepare_data_for_top_lists(df_original)
    # Assert
    assert_frame_equal(df_original, df_copy_before) # Original should be unchanged.
    assert NUM_IND_COL not in df_original.columns # Ensure new column is not added inplace.

##### Test Cases: calculate_all_top_lists #####

# --- Test: Happy Path (top_n = 3) --- #
def test_calculate_all_top_lists_happy_path(top_list_data):
    # Arrange
    top_n = 3 # Set top N for testing.

    # Act
    result = calculate_all_top_lists(top_list_data, top_n=top_n)

    # Assert: Check structure
    assert isinstance(result, dict) # Should return a dictionary.
    expected_keys = [
        "top_species_freq", "top_families_freq", "top_observers_freq",
        "top_individual_obs", "top_redlist_species_agg",
        "top_alien_species_agg", "top_special_species_agg"
    ]
    assert all(key in result for key in expected_keys) # Check all keys exist.

    # Assert: Top Species Freq (Art A:3, Art B:2, Art C:1 / Art D:1 / ...)
    top_species = result["top_species_freq"]
    assert len(top_species) == top_n # Check length.
    assert top_species['Art'].tolist() == ['Art A', 'Art B', 'Art C'] # Check species order.
    assert top_species['Antall_Observasjoner'].tolist() == [3, 2, 1] # Check counts.

    # Assert: Top Families Freq (Fam X:3, Fam Y:3, Fam Z:2)
    top_families = result["top_families_freq"]
    assert len(top_families) == top_n
    # Order might vary between Fam X and Fam Y (both 3), accept either
    assert sorted(top_families['Familie'].tolist()) == sorted(['Fam X', 'Fam Y', 'Fam Z']) # Check families present.
    assert sorted(top_families['Antall_Observasjoner'].tolist(), reverse=True) == [3, 3, 2] # Check counts.

    # Assert: Top Observers Freq (Obs 1:3, Obs 2:3, Obs 5:2)
    top_observers = result["top_observers_freq"]
    assert len(top_observers) == top_n
    assert sorted(top_observers['Innsamler/Observatør'].tolist()) == sorted(['Obs 1', 'Obs 2', 'Obs 5'])
    assert sorted(top_observers['Antall Observasjoner'].tolist(), reverse=True) == [3, 3, 2]

    # Assert: Top Individual Obs (Indices: 7(20), 5(15), 3(12))
    top_inds = result["top_individual_obs"]
    assert len(top_inds) == top_n
    assert top_inds.index.tolist() == [7, 5, 3] # Check indices of rows with highest counts.
    assert top_inds[NUM_IND_COL].tolist() == [20.0, 15.0, 12.0] # Check the counts themselves.
    assert ART_COL in top_inds.columns # Ensure original columns are present.

    # Assert: Aggregated Lists (Example: Redlist CR)
    # Data: Art A (CR, 5), Art A (CR, 8), Art A (CR, 15) -> Art A: Freq 3, Sum 28
    cr_agg = result["top_redlist_species_agg"]['CR']
    assert len(cr_agg) == 1 # Only one species in CR category.
    assert cr_agg.iloc[0][ART_COL] == 'Art A' # Check species.
    assert cr_agg.iloc[0]['Antall_Observasjoner'] == 3 # Check frequency.
    assert cr_agg.iloc[0]['Sum_Individer'] == 28 # Check sum (5+8+15).

    # Assert: Aggregated Lists (Example: Alien SE)
    # Data: Art C (SE, 12), Art F (SE, 2) -> Art C: Freq 1, Sum 12; Art F: Freq 1, Sum 2
    se_agg = result["top_alien_species_agg"]['SE']
    assert len(se_agg) == 2 # Two species in SE category.
    # Sort by Art for consistent checking
    se_agg = se_agg.sort_values(by=ART_COL).reset_index()
    assert se_agg.loc[0, ART_COL] == 'Art C' and se_agg.loc[0, 'Antall_Observasjoner'] == 1 and se_agg.loc[0, 'Sum_Individer'] == 12
    assert se_agg.loc[1, ART_COL] == 'Art F' and se_agg.loc[1, 'Antall_Observasjoner'] == 1 and se_agg.loc[1, 'Sum_Individer'] == 2

    # Assert: Aggregated Lists (Example: Prioriterte Arter)
    # Data: Art A(Yes, 5), Art A(Yes, 8), Art D(Yes, 0), Art E(Yes, 20)
    # -> Art A: Freq 2, Sum 13; Art D: Freq 1, Sum 0; Art E: Freq 1, Sum 20
    prio_agg = result["top_special_species_agg"]["Prioriterte Arter"]
    assert len(prio_agg) == 3 # Top 3 species flagged as Prioriterte Arter.
    # Should be sorted by Freq (desc), then Sum (desc)
    # Art A (Freq 2), Art E (Freq 1, Sum 20), Art D (Freq 1, Sum 0)
    assert prio_agg.iloc[0][ART_COL] == 'Art A' and prio_agg.iloc[0]['Antall_Observasjoner'] == 2 and prio_agg.iloc[0]['Sum_Individer'] == 13
    assert prio_agg.iloc[1][ART_COL] == 'Art E' and prio_agg.iloc[1]['Antall_Observasjoner'] == 1 and prio_agg.iloc[1]['Sum_Individer'] == 20
    assert prio_agg.iloc[2][ART_COL] == 'Art D' and prio_agg.iloc[2]['Antall_Observasjoner'] == 1 and prio_agg.iloc[2]['Sum_Individer'] == 0


# --- Test: Empty Input --- #
def test_calculate_all_top_lists_empty_input(empty_top_list_data):
    # Arrange: Use the empty fixture.
    # Act
    result = calculate_all_top_lists(empty_top_list_data, top_n=5)
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
    # Arrange: Use data with 7 unique species, ask for top 10.
    top_n = 10
    # Act
    result = calculate_all_top_lists(top_list_data, top_n=top_n)
    # Assert
    assert len(result["top_species_freq"]) == 7 # Should return all 7 unique species.
    assert len(result["top_families_freq"]) == 4 # Should return all 4 unique families.
    assert len(result["top_observers_freq"]) == 5 # Should return all 5 unique observers.
    # Top individual obs depends on total rows vs top_n
    assert len(result["top_individual_obs"]) == min(top_n, len(top_list_data)) # Should return min(10, 10) = 10 rows.

# --- Test: Missing Column --- #
def test_calculate_all_top_lists_missing_column(top_list_data):
    # Arrange: Drop a column needed for a specific list (e.g., Familie).
    data_missing_fam = top_list_data.drop(columns=[FAM_COL])
    # Act & Assert: Expect KeyError when calculating top families list.
    with pytest.raises(KeyError) as excinfo:
        calculate_all_top_lists(data_missing_fam, top_n=3)
    assert FAM_COL in str(excinfo.value) # Verify the error message.

# --- Test: No Data for Specific Category --- #
def test_calculate_all_top_lists_no_data_for_category(top_list_data):
    # Arrange: Use standard data, but check a category with no entries (e.g., DD).
    # Act
    result = calculate_all_top_lists(top_list_data, top_n=3)
    # Assert
    assert 'DD' in result["top_redlist_species_agg"] # Key should exist.
    dd_agg = result["top_redlist_species_agg"]['DD']
    assert isinstance(dd_agg, pd.DataFrame) # Should be a DataFrame.
    assert dd_agg.empty # Should be empty.
    assert list(dd_agg.columns) == ['Art', 'Antall_Observasjoner', 'Sum_Individer'] # Should have correct columns. 
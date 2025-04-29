import pandas as pd
from pathlib import Path
#

##### Helper Functions #####

## Function: clean_csv_columns ##
def clean_csv_columns(df):
    # Minimal function: Removes columns based on a predefined list.
    # Input `df` is expected to be a pandas DataFrame.
    """Removes unnecessary columns from the DataFrame."""
    # List of column names to be removed. Modify this list to change which
    # columns are kept/removed.
    # Adding a name removes it, removing a name keeps it.
    columns_to_delete = [
        # Identifiers and internal system data
        'proxyId',
        'nodeId',
        'institutionCode',
        'collectionCode',
        'datasetId',
        'occurrenceId',
        'catalogNumber',
        'otherCatalogNumbers',
        'relatedResourceId',
        'relationshipOfResource',
        'associatedReferences',
        'institution',
        'collection',
        'datasetName',
        # Redundant coordinates
        'east',
        'north',
        # Database/metadata dates
        'dateLastModified',
        'dateLastIdentified',
        # Data quality/system flags
        'hasErrors',
        'blocked',
        'qualityIssue',
        'validated',
        # Complex/redundant fields
        'dynamicProperties',
        'popularNames',
        # Less commonly needed taxonomic/observation details
        'validScientificNameAuthorship',
        'identifiedBy',
        'unspontaneus',
        'unsureIdentification',
        'hasImage',
        'absent',
        'notRecovered',
        'habitat',
        'collectingMethod',
        'recordNumber',
        'fieldNumber',
        'measurementMethod',
        'georeferenceRemarks',
        'preparations',
        'typeStatus',
        'eventTime',
        'maximumElevationInMeters',
        'minimumElevationInMeters',
        'verbatimDepth',
    ]

    # Drops the specified columns. errors='ignore' means it won't fail if
    # a column in the list doesn't exist in the input DataFrame `df`.
    # Change to errors='raise' to get an error for non-existent columns.
    return df.drop(columns=columns_to_delete, errors='ignore')


##### Main Logic #####

## Function: main ##
def main(raw_csv_path, cleaned_csv_path):
    # Minimal function: Reads CSV, cleans columns, writes new CSV.
    # Assumes `raw_csv_path` points to an existing CSV file.
    # Assumes `cleaned_csv_path` is a valid path for writing.

    # --- Load Data (Happy Path Only) ---
    # Reads the CSV. Assumes ';' separator.
    # Modifying sep=';' changes delimiter. Assumes file exists and is readable.
    df_raw = pd.read_csv(raw_csv_path, sep=';')

    # --- Clean Columns ---
    # Calls the helper function to remove columns based on the hardcoded list.
    # Result `cleaned_df` is a DataFrame with fewer columns.
    cleaned_df = clean_csv_columns(df_raw)

    # --- Process individualCount Column ---
    # The column is assumed to exist after the cleaning step.
    # Fill missing values (NaN) with 1.
    # inplace=False by default, so it returns a new Series/DataFrame.
    cleaned_df['individualCount'] = cleaned_df['individualCount'].fillna(1)
    # Convert the column to nullable integer type ('Int64').
    # Using 'Int64' (capital I) handles potential NA values if needed,
    # though fillna(1) should prevent them in this specific case.
    cleaned_df['individualCount'] = cleaned_df['individualCount'].astype('Int64')

    # --- Save Result ---
    # Saves cleaned data to the specified path. Assumes path is valid/writable.
    # index=False prevents writing the DataFrame index as a column in the CSV.
    # sep=';' sets the output delimiter. Change as needed.
    cleaned_df.to_csv(cleaned_csv_path, index=False, sep=';')

    # Return the output path (core function result).
    # This indicates where the cleaned file was saved.
    return cleaned_csv_path


##### Execution Entry Point #####

if __name__ == "__main__":
    # Minimal block, no default action for direct run.
    pass  # Keeping pass as no default action is defined for direct run.
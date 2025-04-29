import pandas as pd
from pathlib import Path

def clean_csv_columns(df):
    """Removes unnecessary columns from the DataFrame."""
    # Define columns to remove
    columns_to_delete = [
        # Identifiers and internal system data
        'proxyId', 'nodeId', 'institutionCode', 'collectionCode', 
        'datasetId', 'occurrenceId', 'catalogNumber', 'otherCatalogNumbers',
        'relatedResourceId', 'relationshipOfResource', 'associatedReferences',
        'validScientificNameId',
        'institution',
        'collection',
        # 'collector' - Keep this column for network analysis
        'datasetName',
        # Redundant coordinates
        'east', 'north',
        # Database/metadata dates
        'dateLastModified', 'dateLastIdentified',
        # Data quality/system flags
        'hasErrors', 'blocked', 'qualityIssue', 'validated',
        # Complex/redundant fields
        'dynamicProperties', 'popularNames',
        # Less commonly needed taxonomic/observation details
        'validScientificNameAuthorship', 'identifiedBy', 'unspontaneus',
        'unsureIdentification', 'hasImage', 'absent', 'notRecovered',
        'habitat', 'collectingMethod', 'recordNumber', 'fieldNumber',
        'measurementMethod', 'georeferenceRemarks', 'preparations',
        'typeStatus', 'eventTime', 'maximumElevationInMeters',
        'minimumElevationInMeters', 'verbatimDepth',
    ]

    return df.drop(columns=columns_to_delete, errors='ignore')

def main(raw_csv_path: Path, cleaned_csv_path: Path) -> Path | None:
    """Process the CSV file and save the cleaned version."""
    
    print(f"Loading {raw_csv_path}...")
    
    # Load, clean and save in a simple flow
    try:
        df_raw = pd.read_csv(raw_csv_path, sep=';')
        cleaned_df = clean_csv_columns(df_raw)
        cleaned_df.to_csv(cleaned_csv_path, index=False, sep=';')
        print(f"Successfully saved cleaned data to {cleaned_csv_path}")
        return cleaned_csv_path
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":

    print("Running cleaner script directly requires manual path configuration.")

    pass # Prevent direct execution without paths
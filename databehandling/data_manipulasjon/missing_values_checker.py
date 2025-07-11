"""
Missing Values Checker for Species Data
Checks for missing preferredPopularName values and prompts user to fill them interactively.
"""

import pandas as pd
import sys
from pathlib import Path
from typing import Optional, Tuple

def check_missing_popular_names(input_csv_path: Path, output_csv_path: Path) -> Optional[Path]:
    """
    Check for missing preferredPopularName values and prompt user to fill them.
    
    Args:
        input_csv_path: Path to input CSV file
        output_csv_path: Path where the updated CSV should be saved
        
    Returns:
        Path to output file if successful, None if failed or cancelled
    """
    try:
        # Read CSV with semicolon delimiter
        print(f"Reading CSV file: {input_csv_path}")
        df = pd.read_csv(input_csv_path, sep=';', encoding='utf-8-sig')
        
        # Check if required columns exist
        required_columns = ['preferredPopularName', 'validScientificName']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            print(f"Error: Missing required columns: {missing_cols}")
            return None
            
        # Find rows with missing preferredPopularName
        missing_mask = df['preferredPopularName'].isna() | (df['preferredPopularName'].str.strip() == '')
        missing_rows = df[missing_mask].copy()
        
        if len(missing_rows) == 0:
            print("No missing preferredPopularName values found. Copying file to output location.")
            # Copy file to output location even if no changes needed
            df.to_csv(output_csv_path, sep=';', index=False, encoding='utf-8-sig')
            return output_csv_path
            
        # Group missing rows by scientific name to avoid duplicate prompts
        unique_missing_species = missing_rows['validScientificName'].unique()
        
        print(f"\nFound {len(missing_rows)} rows with missing preferredPopularName values.")
        print(f"Found {len(unique_missing_species)} unique species missing popular names.")
        print("Please provide popular names for the following species:")
        print("Commands: Enter name, 's' to skip, 'q' to quit\n")
        
        changes_made = 0
        species_mapping = {}  # Store user responses for each species
        
        # First, collect popular names for each unique species
        for scientific_name in unique_missing_species:
            count = len(missing_rows[missing_rows['validScientificName'] == scientific_name])
            
            while True:
                response = input(f"Scientific name: '{scientific_name}' ({count} rows) - Enter popular name (or 's'/'q'): ").strip()
                
                if response.lower() == 'q':
                    print("Operation cancelled by user.")
                    return None
                elif response.lower() == 's':
                    print("Skipped.")
                    species_mapping[scientific_name] = None  # Mark as skipped
                    break
                elif response:
                    species_mapping[scientific_name] = response
                    print(f"Will apply '{response}' to {count} rows")
                    break
                else:
                    print("Please enter a valid name, 's' to skip, or 'q' to quit.")
        
        # Apply the collected popular names to all matching rows
        for scientific_name, popular_name in species_mapping.items():
            if popular_name is not None:  # Skip if user chose to skip this species
                matching_rows = df['validScientificName'] == scientific_name
                missing_matching_rows = matching_rows & missing_mask
                df.loc[missing_matching_rows, 'preferredPopularName'] = popular_name
                changes_made += len(df[missing_matching_rows])
        
        # Save the updated dataframe
        print(f"\nSaving updated CSV with {changes_made} changes to: {output_csv_path}")
        df.to_csv(output_csv_path, sep=';', index=False, encoding='utf-8-sig')
        
        return output_csv_path
        
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return None

def main(input_csv_path: Path, output_csv_path: Path) -> Optional[Path]:
    """
    Main function to check and fill missing popular names.
    
    Args:
        input_csv_path: Path to input CSV file
        output_csv_path: Path where the updated CSV should be saved
        
    Returns:
        Path to output file if successful, None if failed
    """
    # Ensure output directory exists
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    return check_missing_popular_names(input_csv_path, output_csv_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python missing_values_checker.py <input_csv> <output_csv>")
        sys.exit(1)
        
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.")
        sys.exit(1)
        
    result = main(input_path, output_path)
    if result:
        print(f"Success: Updated file saved to {result}")
    else:
        print("Failed to process file.")
        sys.exit(1)
##### Imports #####
import csv # Import the csv module for reading CSV files

##### Constants #####
INPUT_CSV_PATH = "databehandling/output/fuglsortland_taxonomy.csv" # Path to the input CSV file
OUTPUT_MD_PATH = "databehandling/output/possible_values_output.md" # Path for the output markdown file

##### Functions #####
def analyze_csv_values(csv_path, md_path):
    # Reads a CSV file, finds unique values for each column, and writes them to a markdown file.
    # Assumes the first row is the header and the delimiter is ';'.

    # --- Initialize Data Structures ---
    unique_values = {} # Dictionary to hold sets of unique values for each column
    column_names = [] # List to store the header names in order

    # --- Read CSV and Collect Unique Values ---
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as infile: # Open the CSV file for reading
            reader = csv.reader(infile, delimiter=';') # Create a CSV reader object with semicolon delimiter

            column_names = next(reader) # Read the first line as the header
            for name in column_names: # Iterate through header names
                unique_values[name] = set() # Initialize an empty set for each column

            for row in reader: # Iterate through the rest of the rows in the CSV
                if len(row) == len(column_names): # Basic check if row length matches header length
                    for i, value in enumerate(row): # Iterate through values in the current row
                        column_name = column_names[i] # Get the corresponding column name
                        unique_values[column_name].add(value.strip()) # Add the stripped value to the set for that column
                # else: # Optional: Handle rows with incorrect number of columns (omitted for simplicity now)
                    # print(f"Skipping row with unexpected number of columns: {row}")

    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {csv_path}") # Print error if file not found
        return # Exit the function if file is not found
    except Exception as e:
        print(f"An error occurred while reading the CSV: {e}") # Print any other reading errors
        return # Exit the function on other errors

    # --- Write Unique Values to Markdown ---
    try:
        with open(md_path, mode='w', encoding='utf-8') as outfile: # Open the markdown file for writing
            outfile.write("# Possible Values per Column\n\n") # Write the main title

            for name in column_names: # Iterate through columns in their original order
                outfile.write(f"## {name}\n\n") # Write the column name as a level 2 header
                values_list = sorted(list(unique_values[name])) # Convert the set to a sorted list
                for value in values_list: # Iterate through the sorted unique values
                    outfile.write(f"- `{value}`\n") # Write each value as a list item, formatted as inline code
                outfile.write("\n") # Add a newline for spacing between columns

        print(f"Successfully wrote unique values to {md_path}") # Confirmation message

    except Exception as e:
        print(f"An error occurred while writing the markdown file: {e}") # Print any writing errors

##### Main Execution #####
if __name__ == "__main__":
    analyze_csv_values(INPUT_CSV_PATH, OUTPUT_MD_PATH) # Call the main analysis function

import pandas as pd
import requests  # External library for making HTTP requests
from tqdm import tqdm  # Import tqdm for progress bar

# Base URL for the NorTaxa API.
NORTAXA_API_BASE_URL = "https://nortaxa.artsdatabanken.no/api/v1/TaxonName"

# ----------------------------------------
# Fetches taxon data for a given scientificNameId from the NorTaxa API.
# ----------------------------------------


def fetch_taxon_data(scientific_name_id):
    api_url = f"{NORTAXA_API_BASE_URL}/ByScientificNameId/{scientific_name_id}"
    # Make a GET request to the API with a timeout of 10 seconds.
    response = requests.get(api_url, timeout=10)

    # Minimal: Assumes a 200 OK response and valid JSON.
    # Does not check response.status_code or handle non-JSON responses.
    if response.ok:  # Basic check if status code is < 400
        return response.json()  # Return the parsed JSON data.
    else:
        # In minimal form, return None on failure. Robust version would log/raise.
        return None  # Indicate failure to fetch or non-OK status.


## Function: extract_hierarchy ##
def extract_hierarchy(api_data):
    # Extracts taxonomic hierarchy, Family ID, and Order ID from API data.
    # Assumes 'higherClassification' exists and has the expected structure.
    """Extracts hierarchy, family ID, and order ID from API data dictionary."""
    hierarchy = {}  # Dictionary to store ranks: {RankName: ScientificName}.
    family_id = None  # Variable to store the scientificNameId of the Family rank.
    order_id = None  # Variable to store the scientificNameId of the Order rank.
    # Define the desired ranks to extract. Modify if other ranks are needed.
    desired_ranks = ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus"]

    # Check if 'higherClassification' key exists in the data.
    if api_data and "higherClassification" in api_data:
        # Iterate through the classification levels in the API response.
        for level in api_data["higherClassification"]:
            rank = level.get("taxonRank")  # Get the rank name (e.g., 'Kingdom').
            name = level.get("scientificName")  # Get the scientific name for the rank.
            current_level_id = level.get("scientificNameId")  # Get the ID for this level.
            # If the rank is one we desire, store it.
            if rank in desired_ranks:
                hierarchy[rank] = name  # Store as {Rank: Name}.
            # If this level is the Family, store its scientificNameId.
            if rank == "Family":
                family_id = current_level_id  # Get the ID for family lookup.
            # If this level is the Order, store its scientificNameId.
            if rank == "Order":
                order_id = current_level_id  # Get the ID for order lookup.

    # Return the extracted hierarchy dictionary, family ID, and order ID.
    return hierarchy, family_id, order_id


## Function: extract_norwegian_vernacular_name ##
def extract_norwegian_vernacular_name(rank_api_data):
    # Extracts the Norwegian vernacular name for a given rank's API data.
    # Assumes 'vernacularNames' exists. Prioritizes Bokmål ('nb').
    """Extracts Norwegian vernacular name from a rank's API data dictionary."""
    # Check if 'vernacularNames' key exists in the data.
    if rank_api_data and "vernacularNames" in rank_api_data:
        # Iterate through the list of vernacular names.
        for name_info in rank_api_data["vernacularNames"]:
            # Check if the language is Bokmål ('nb').
            if name_info.get("languageIsoCode") == "nb":
                # Return the Bokmål name if found.
                return name_info.get("vernacularName")
        # If no Bokmål name, check for Nynorsk ('nn') as a fallback.
        for name_info in rank_api_data["vernacularNames"]:
            if name_info.get("languageIsoCode") == "nn":
                # Return the Nynorsk name if found.
                return name_info.get("vernacularName")
    # Return None if no relevant vernacular name is found.
    return None  # Indicate failure to find a Norwegian name.


##### Main Logic #####


## Function: main ##
def main(input_csv_path, output_csv_path):
    # Main function to add taxonomy columns to the CSV.
    # Reads input, fetches data from API, merges, and saves output.
    # Assumes input CSV exists and contains 'validScientificNameId'.

    # --- Load Input Data ---
    # Load the CSV file processed by previous steps. Assumes ';' separator.
    df = pd.read_csv(input_csv_path, sep=";")
    # Ensure the required ID column exists (minimal check).
    if "validScientificNameId" not in df.columns:
        # Minimal error indication. Robust version would raise/log.
        # print("Error: 'validScientificNameId' column not found in input CSV.")
        return None  # Stop processing if essential column is missing.

    # Get unique IDs to minimize API calls. Drop NaNs just in case.
    unique_ids = df["validScientificNameId"].dropna().unique()

    # --- Fetch Data from API (for unique IDs) ---
    # Dictionaries to store fetched data, keyed by species scientificNameId.
    taxonomy_data = {}  # Stores {species_id: {'Kingdom': '...', ...}}
    family_names_data = {}  # Stores {species_id: 'Norwegian Family Name'}
    order_names_data = {}  # Stores {species_id: 'Norwegian Order Name'}

    # --- Loop through IDs with Progress Bar ---
    # Wrap the unique_ids iterable with tqdm for a progress bar.
    # `desc` sets the label, `unit` clarifies what each iteration represents.
    print("Fetching taxonomy data from API...")  # Add context print before bar
    for species_id in tqdm(unique_ids, desc="Fetching Taxonomy", unit="ID"):
        # Convert ID to integer if necessary, handle potential errors minimally.
        try:
            current_id = int(species_id)  # Ensure ID is integer type for API call.
        except ValueError:
            # Skip if ID is not a valid integer. Robust version would log this.
            continue  # Move to the next ID.

        # Fetch the main taxon data for the species ID.
        species_data = fetch_taxon_data(current_id)
        # Process the species data if the fetch was successful.
        if species_data:
            # Extract the hierarchy, Family ID, and Order ID.
            hierarchy, family_id, order_id = extract_hierarchy(species_data)
            # Store the extracted hierarchy keyed by the species ID.
            taxonomy_data[current_id] = hierarchy

            # If a valid family ID was found, fetch the family's data.
            if family_id:
                family_data = fetch_taxon_data(family_id)
                # If family data fetched successfully, extract the Norwegian name.
                if family_data:
                    norwegian_family_name = extract_norwegian_vernacular_name(family_data)
                    # Store the Norwegian name keyed by the original species ID.
                    family_names_data[current_id] = norwegian_family_name

            # If a valid order ID was found, fetch the order's data.
            if order_id:
                order_data = fetch_taxon_data(order_id)
                # If order data fetched successfully, extract the Norwegian name.
                if order_data:
                    norwegian_order_name = extract_norwegian_vernacular_name(order_data)
                    # Store the Norwegian name keyed by the original species ID.
                    order_names_data[current_id] = norwegian_order_name

    # --- Merge API Data into DataFrame ---
    # Map the fetched hierarchy data to the corresponding rows using species ID.
    # Creates a temporary column containing the hierarchy dictionaries.
    df["temp_hierarchy"] = df["validScientificNameId"].map(taxonomy_data)

    # Extract each taxonomic rank into its own new column.
    # Define the ranks we expect to extract from the hierarchy dict.
    ranks_to_extract = ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus"]
    for rank in ranks_to_extract:
        # Apply a function to get the rank value from the dict, handle missing data.
        df[rank] = df["temp_hierarchy"].apply(lambda x: x.get(rank, None) if isinstance(x, dict) else None)

    # Map the fetched Norwegian family and order names.
    df["FamilieNavn"] = df["validScientificNameId"].map(family_names_data)
    df["OrdenNavn"] = df["validScientificNameId"].map(order_names_data)

    # Remove the temporary hierarchy dictionary column.
    df = df.drop(columns=["temp_hierarchy"])

    # --- Save Result ---
    # Saves the enriched DataFrame to the specified output path.
    # Assumes path is valid/writable. index=False prevents writing index.
    df.to_csv(output_csv_path, index=False, sep=";")

    # Return the output path indicating successful completion.
    return output_csv_path


##### Execution Entry Point #####

if __name__ == "__main__":
    # Minimal block, no default action for direct run.
    # Example of how to call main (requires manual path setting):
    # INPUT_PATH = "path/to/intermediate_processed.csv"
    # OUTPUT_PATH = "path/to/final_taxonomy_output.csv"
    # result = main(INPUT_PATH, OUTPUT_PATH)
    # if result:
    #     print(f"Processing complete. Output saved to: {result}")
    pass  # Keeping pass as no default action is defined for direct run.

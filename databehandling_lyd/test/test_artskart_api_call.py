import sys
from pathlib import Path

# Add the project's root directory (databehandling_lyd) to the Python path
# This allows Python to find the 'functions' module
script_dir = Path(__file__).resolve().parent
project_root_dir = script_dir.parent  # This should be 'databehandling_lyd'
sys.path.insert(0, str(project_root_dir))

import json
import logging
from functions.artskart_api import fetch_artskart_taxon_info_by_name

# Configure basic logging to see output from the API function
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

# --- !!! IMPORTANT !!! ---
# Change this to the scientific name you want to test
scientific_name_to_test = "Cyanistes caeruleus"  # Example: Blue Tit
# ---

if __name__ == "__main__":
    if not scientific_name_to_test or scientific_name_to_test == "REPLACE_WITH_SCIENTIFIC_NAME":
        print("Please edit the script and set the 'scientific_name_to_test' variable.")
    else:
        print(f"Testing Artskart API with scientific name: {scientific_name_to_test}")

        taxon_info = fetch_artskart_taxon_info_by_name(scientific_name_to_test)

        if taxon_info:
            print("\n--- API Response ---")
            print(json.dumps(taxon_info, indent=2, ensure_ascii=False))  # Pretty print the JSON

            # Specifically check for PopularNames and Norwegian names
            popular_names = taxon_info.get("PopularNames")
            if popular_names:
                print("\n--- Popular Names Extracted ---")
                norwegian_name_found = False
                for pop_name in popular_names:
                    if isinstance(pop_name, dict) and pop_name.get("language", "").lower().startswith("nb"):
                        print(
                            f"  Norwegian Name (Bokmål): {pop_name.get('Name')}, Preferred: {pop_name.get('Preffered')}"
                        )  # Note: 'Preffered' typo matches your code
                        norwegian_name_found = True
                if not norwegian_name_found:
                    print("  No Norwegian (Bokmål) name found in PopularNames.")
            else:
                print("\n--- Popular Names ---")
                print("No 'PopularNames' field in the API response.")

        else:
            print("\n--- No information returned from API for this scientific name ---")

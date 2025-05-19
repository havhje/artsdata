from pathlib import Path
import pandas as pd
import functools
import multiprocessing
from functions.birdnetlib_api import run_birdnet_analysis, on_analyze_directory_complete

# Import functions from artskart_api
from functions.artskart_api import fetch_artskart_taxon_info_by_name
from functions.splitter_lydfilen import split_audio_by_detection  # Added import
import logging  # Import logging
from tqdm import tqdm  # Import tqdm for progress bar

# ----------------------------------------
# Setup Logging
# ----------------------------------------
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)

# ----------------------------------------
# Lager relativ sti til input_dir
# ----------------------------------------

# Get the directory where the current script is located.
script_dir = Path(__file__).resolve().parent
# Construct the path to data_input_lyd relative to the script's directory.
input_directory_path = script_dir / "data_input_lyd"
# Construct the path for the output CSV file.
output_csv_path = script_dir / "data_output_lyd" / "interim" / "enriched_detections.csv"
# Ensure the output directory exists
output_csv_path.parent.mkdir(parents=True, exist_ok=True)

# Define the output directory for split audio files
split_audio_output_dir = script_dir / "data_output_lyd" / "lydfiler"

# ---------------------------------------
# Konfigurasjon for audiosplitting
# ---------------------------------------

# Set this flag to False if you want to skip audio splitting
RUN_AUDIO_SPLITTING = False

prepared_callback_function = functools.partial(on_analyze_directory_complete, base_input_path=input_directory_path)

# ---------------------------------------
# Lager en pd-dataframe fra listen med deteksjoner fra BirdNET
# ----------------------ß


def initialize_dataframe(detections_list: list) -> pd.DataFrame | None:
    """Converts a list of detections to a DataFrame and initializes required columns."""
    if not detections_list:
        logging.info("No detections were found.")
        return None

    df = pd.DataFrame(detections_list)

    # Expect 'scientific_name' from BirdNET. This will be used to fetch 'validScientificNameId'.
    if "scientific_name" not in df.columns:
        logging.error("'scientific_name' column not found in detections. This is required for taxonomic enrichment.")
        # Optionally, return None or an empty DataFrame if this is a critical error
        return df

    # Initialize 'validScientificNameId' which will be populated.
    df["validScientificNameId"] = pd.NA

    # Initialize columns for taxonomic enrichment
    df["Species_NorwegianName"] = pd.NA
    df["Family_ScientificName"] = pd.NA
    df["Family_NorwegianName"] = pd.NA
    df["Order_ScientificName"] = pd.NA
    df["Order_NorwegianName"] = pd.NA
    df["Family_ScientificNameId"] = pd.NA
    df["Order_ScientificNameId"] = pd.NA
    df["Species_ScientificNameId"] = pd.NA
    df["Redlist_Status"] = pd.NA  # Add new column for Red List status
    return df


def get_norwegian_popular_name(popular_names_list: list) -> str | None:
    if not popular_names_list or not isinstance(popular_names_list, list):
        return None
    # First pass: look for a preferred Bokmål name
    for pop_name_info in popular_names_list:
        if isinstance(pop_name_info, dict):
            lang = pop_name_info.get("language", "").lower()
            if lang.startswith("nb") and pop_name_info.get("Preffered", False):
                return pop_name_info.get("Name")
    # Second pass: look for any Bokmål name if no preferred one was found
    for pop_name_info in popular_names_list:
        if isinstance(pop_name_info, dict):
            lang = pop_name_info.get("language", "").lower()
            if lang.startswith("nb"):
                return pop_name_info.get("Name")
    return None


def enrich_detections_with_taxonomy(df: pd.DataFrame) -> pd.DataFrame:
    """Enriches the detections DataFrame with taxonomic information using Artskart API."""
    if "scientific_name" not in df.columns or df["scientific_name"].isnull().all():
        logging.warning("Skipping taxonomic enrichment: 'scientific_name' column is missing or all null.")
        return df

    unique_scientific_names = df["scientific_name"].dropna().unique()
    # Cache for taxon info fetched from Artskart to avoid redundant API calls
    # Key: scientific_name_str, Value: taxon_info_dict from Artskart
    artskart_info_cache = {}

    logging.info(f"Fetching Artskart taxon info for {len(unique_scientific_names)} unique scientific names...")
    for name in tqdm(unique_scientific_names, desc="Fetching Artskart Data", unit="name"):
        if name not in artskart_info_cache:
            try:
                taxon_info = fetch_artskart_taxon_info_by_name(name)
                artskart_info_cache[name] = taxon_info  # Cache the result, even if None
                if not taxon_info:
                    logging.warning(f"No Artskart data found for scientific name: {name}")
            except Exception as e:
                logging.error(f"Error fetching Artskart data for '{name}': {e}", exc_info=True)
                artskart_info_cache[name] = None  # Cache None on error

    # --- Apply fetched data to the DataFrame ---
    # Create temporary lists to hold new column data
    valid_ids_list = []
    species_nor_names_list = []
    family_sci_names_list = []
    order_sci_names_list = []
    redlist_status_list = []  # New list for Red List statuses
    # species_sci_name_id_list = [] # This will be same as valid_ids_list

    for index, row in df.iterrows():
        sci_name = row["scientific_name"]
        taxon_info = artskart_info_cache.get(sci_name)

        if taxon_info and isinstance(taxon_info, dict):
            valid_id = taxon_info.get("ValidScientificNameId")
            valid_ids_list.append(valid_id if valid_id is not None else pd.NA)
            # species_sci_name_id_list.append(valid_id if valid_id is not None else pd.NA)

            popular_names_species = taxon_info.get("PopularNames")
            species_nor_name = get_norwegian_popular_name(popular_names_species)
            if not species_nor_name and sci_name:  # Added sci_name check for context
                logging.info(
                    f"No Norwegian species name found for '{sci_name}'. PopularNames from API: {popular_names_species}"
                )
            species_nor_names_list.append(species_nor_name if species_nor_name else pd.NA)

            family_sci_names_list.append(taxon_info.get("Family", pd.NA))
            order_sci_names_list.append(taxon_info.get("Order", pd.NA))
            redlist_status_list.append(taxon_info.get("Status", pd.NA))  # Populate Red List status
        else:
            valid_ids_list.append(pd.NA)
            # species_sci_name_id_list.append(pd.NA)
            species_nor_names_list.append(pd.NA)
            family_sci_names_list.append(pd.NA)
            order_sci_names_list.append(pd.NA)
            redlist_status_list.append(pd.NA)  # Append NA if no taxon_info

    df["validScientificNameId"] = valid_ids_list
    df["Species_ScientificNameId"] = valid_ids_list  # Alias for clarity
    df["Species_NorwegianName"] = species_nor_names_list
    df["Family_ScientificName"] = family_sci_names_list
    df["Order_ScientificName"] = order_sci_names_list
    df["Redlist_Status"] = redlist_status_list  # Assign the new column

    # --- Process Redlist_Status to keep only the first value ---
    # If Redlist_Status contains a comma, split by it and take the first part.
    df["Redlist_Status"] = df["Redlist_Status"].apply(
        lambda x: x.split(",")[0].strip() if isinstance(x, str) and "," in x else x
    )

    # --- Now, handle Norwegian names for Family and Order ---
    # This requires a second pass: get unique Family/Order scientific names
    # then fetch their Artskart info to get their Norwegian popular names.

    unique_family_names = df["Family_ScientificName"].dropna().unique()
    family_nor_names_cache = {}  # Cache for Family SciName -> Norwegian Name

    logging.info(f"Fetching Norwegian names for {len(unique_family_names)} unique families...")
    for fam_name in tqdm(unique_family_names, desc="Fetching Family Names", unit="fam"):
        if (
            fam_name not in artskart_info_cache
        ):  # Check if already fetched (e.g. if a family name was also a species name)
            taxon_info_fam = fetch_artskart_taxon_info_by_name(fam_name)
            artskart_info_cache[fam_name] = taxon_info_fam  # Add to main cache
        else:
            taxon_info_fam = artskart_info_cache[fam_name]

        if taxon_info_fam:
            popular_names_family = taxon_info_fam.get("PopularNames")
            norwegian_name_for_family = get_norwegian_popular_name(popular_names_family)
            family_nor_names_cache[fam_name] = norwegian_name_for_family
            if not norwegian_name_for_family:
                logging.info(
                    f"No Norwegian name found for family '{fam_name}'. PopularNames from API: {popular_names_family}"
                )
        else:
            family_nor_names_cache[fam_name] = None
            logging.warning(f"Could not fetch details for family: {fam_name} to get Norwegian name.")

    df["Family_NorwegianName"] = df["Family_ScientificName"].map(family_nor_names_cache).fillna(pd.NA)

    unique_order_names = df["Order_ScientificName"].dropna().unique()
    order_nor_names_cache = {}  # Cache for Order SciName -> Norwegian Name

    logging.info(f"Fetching Norwegian names for {len(unique_order_names)} unique orders...")
    for ord_name in tqdm(unique_order_names, desc="Fetching Order Names", unit="ord"):
        if ord_name not in artskart_info_cache:
            taxon_info_ord = fetch_artskart_taxon_info_by_name(ord_name)
            artskart_info_cache[ord_name] = taxon_info_ord
        else:
            taxon_info_ord = artskart_info_cache[ord_name]

        if taxon_info_ord:
            popular_names_order = taxon_info_ord.get("PopularNames")
            norwegian_name_for_order = get_norwegian_popular_name(popular_names_order)
            order_nor_names_cache[ord_name] = norwegian_name_for_order
            if not norwegian_name_for_order:
                logging.info(
                    f"No Norwegian name found for order '{ord_name}'. PopularNames from API: {popular_names_order}"
                )
        else:
            order_nor_names_cache[ord_name] = None

    df["Order_NorwegianName"] = df["Order_ScientificName"].map(order_nor_names_cache).fillna(pd.NA)

    # Columns for Family_ScientificNameId and Order_ScientificNameId are still NA
    # as the current API call for species doesn't directly provide IDs for its family/order.
    # If these IDs are needed, a similar loop to fetch them for unique family/order names would be required.
    # For now, we have the Norwegian names.

    logging.info("Taxonomic enrichment completed.")
    return df


# ----------------------------------------
# Main function
# ----------------------------------------


def main():
    logging.info(
        f"Starting BirdNET analysis on input directory: {input_directory_path}"
    )  # Log the input directory path
    all_detections_list = run_birdnet_analysis(input_directory_path, prepared_callback_function)
    # logging.info(f"Raw detections returned from BirdNET analysis: {all_detections_list}")  # Log the raw detections -- THIS LINE WILL BE COMMENTED OUT/REMOVED

    detections_df = initialize_dataframe(all_detections_list)
    if detections_df is None:
        logging.info("Exiting: No detections to process.")
        return

    logging.info(f"Successfully converted {len(detections_df)} detections to DataFrame.")

    detections_df = enrich_detections_with_taxonomy(detections_df)

    # Save the enriched DataFrame
    try:
        detections_df.to_csv(output_csv_path, index=False, sep=";")
        logging.info(f"Enriched detections saved to: {output_csv_path}")
    except Exception as e:
        logging.error(f"Failed to save enriched detections to CSV: {e}", exc_info=True)

    # After saving the CSV, split the audio files if the flag is True
    if RUN_AUDIO_SPLITTING:
        if detections_df is not None and not detections_df.empty:
            logging.info("Proceeding to split audio files based on detections.")
            split_audio_by_detection(detections_df, split_audio_output_dir)  # Added call
        else:
            logging.info("Skipping audio splitting as there are no detections or DataFrame is empty.")
    else:
        logging.info("Audio splitting is disabled by configuration.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

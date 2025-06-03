"""Modul for å fylle manglende norske populærnavn via Artskart API."""

import pandas as pd
import requests
from tqdm import tqdm
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Constants
ARTSKART_API_BASE_URL = "https://artskart.artsdatabanken.no/publicapi/api"
# Assuming 'validScientificName' column holds the integer ID for the API call
# and 'preferredPopularName' is the column to fill.
ID_COLUMN = "validScientificNameId"
POPULAR_NAME_COLUMN = "preferredPopularName"


def fetch_taxon_data(taxon_id: int) -> Optional[Dict[str, Any]]:
    """Henter taksondata fra Artskart API for en gitt takson-ID.

    Args:
        taxon_id: Den numeriske ID-en til taksonet (fra 'validScientificName').

    Returns:
        En dictionary med API-responsen (JSON) hvis vellykket, ellers None.
    """
    print(f"DEBUG: fetch_taxon_data called with taxon_id: {taxon_id}")
    if not taxon_id or pd.isna(taxon_id):
        print(
            f"DEBUG: fetch_taxon_data - Invalid taxon_id (None or NaN): {taxon_id}"
        )
        return None
    try:
        numeric_taxon_id = int(taxon_id)
        api_url = f"{ARTSKART_API_BASE_URL}/taxon/{numeric_taxon_id}"
        print(f"DEBUG: fetch_taxon_data - Calling API URL: {api_url}")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print(
            f"DEBUG: fetch_taxon_data - API call successful for ID {numeric_taxon_id}"
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        print(
            f"DEBUG: fetch_taxon_data - API RequestException for ID {taxon_id}: {e}"
        )
        return None
    except ValueError as e:
        print(
            f"DEBUG: fetch_taxon_data - ValueError (invalid ID format?) for {taxon_id}: {e}"
        )
        return None


def extract_norwegian_popular_name(taxon_data: Dict[str, Any]) -> Optional[str]:
    """Ekstraherer det norske populærnavnet fra API-responsen.

    Prioriterer 'PrefferedPopularname', deretter søker i 'PopularNames'.

    Args:
        taxon_data: Parsed JSON-respons fra Artskart API for et takson.

    Returns:
        Det norske populærnavnet som en streng hvis funnet, ellers None.
    """
    print(
        f"DEBUG: extract_norwegian_popular_name called with taxon_data: {str(taxon_data)[:200]}..."
    )  # Log snippet
    if not taxon_data:
        print("DEBUG: extract_norwegian_popular_name - No taxon_data provided.")
        return None

    preferred_pop_name = taxon_data.get("PrefferedPopularname")
    print(
        f"DEBUG: extract_norwegian_popular_name - API PrefferedPopularname: '{preferred_pop_name}'"
    )
    if (
        preferred_pop_name
        and isinstance(preferred_pop_name, str)
        and preferred_pop_name.strip()
    ):
        print(
            f"DEBUG: extract_norwegian_popular_name - Returning direct PrefferedPopularname: '{preferred_pop_name.strip()}'"
        )
        return preferred_pop_name.strip()

    popular_names_list = taxon_data.get("PopularNames", [])
    print(
        f"DEBUG: extract_norwegian_popular_name - API PopularNames list: {popular_names_list}"
    )
    if not isinstance(popular_names_list, list):
        print(
            "DEBUG: extract_norwegian_popular_name - PopularNames is not a list."
        )
        return None

    norwegian_names = []
    preferred_nb_name = None
    any_nb_name = None

    for name_info in popular_names_list:
        if isinstance(name_info, dict) and name_info.get("language") == "nb":
            name_value = name_info.get("name")
            if (
                name_value
                and isinstance(name_value, str)
                and name_value.strip()
            ):
                print(
                    f"DEBUG: extract_norwegian_popular_name - Found Norwegian name in list: '{name_value.strip()}', Preferred: {name_info.get('Preffered')}"
                )
                if name_info.get("Preffered") is True:
                    preferred_nb_name = name_value.strip()
                    break  # Found the explicitly preferred Norwegian name
                if not any_nb_name:  # Keep the first Norwegian name found
                    any_nb_name = name_value.strip()

    if preferred_nb_name:
        print(
            f"DEBUG: extract_norwegian_popular_name - Returning preferred Norwegian name from list: '{preferred_nb_name}'"
        )
        return preferred_nb_name
    if any_nb_name:
        print(
            f"DEBUG: extract_norwegian_popular_name - Returning first Norwegian name found in list: '{any_nb_name}'"
        )
        return any_nb_name

    print(
        "DEBUG: extract_norwegian_popular_name - No suitable Norwegian name found."
    )
    return None


def fill_missing_popular_names(df: pd.DataFrame) -> pd.DataFrame:
    """Identifiserer rader med manglende populærnavn og fyller dem via API.

    Args:
        df: Pandas DataFrame som skal behandles.
            Forventer kolonner definert av ID_COLUMN og POPULAR_NAME_COLUMN.

    Returns:
        Pandas DataFrame med manglende populærnavn oppdatert.
    """
    print("DEBUG: fill_missing_popular_names called.")
    if ID_COLUMN not in df.columns:
        print(
            f"DEBUG: fill_missing_popular_names - Error: ID column '{ID_COLUMN}' not found in DataFrame."
        )
        return df
    print(f"DEBUG: fill_missing_popular_names - ID column '{ID_COLUMN}' found.")

    if POPULAR_NAME_COLUMN not in df.columns:
        print(
            f"DEBUG: fill_missing_popular_names - Error: Popular name column '{POPULAR_NAME_COLUMN}' not found."
        )
        return df
    print(
        f"DEBUG: fill_missing_popular_names - Popular name column '{POPULAR_NAME_COLUMN}' found."
    )

    missing_mask = (
        df[POPULAR_NAME_COLUMN].isnull()
        | (df[POPULAR_NAME_COLUMN] == "")
        | (df[POPULAR_NAME_COLUMN].astype(str).str.strip() == "")
    )
    print(
        f"DEBUG: fill_missing_popular_names - Missing mask created. Example of POPULAR_NAME_COLUMN before check:\n{df[POPULAR_NAME_COLUMN].head()}"
    )

    rows_to_update = df[missing_mask]

    if rows_to_update.empty:
        print(
            "DEBUG: fill_missing_popular_names - No missing popular names to fill."
        )
        return df

    print(
        f"DEBUG: fill_missing_popular_names - Found {len(rows_to_update)} rows with missing popular names. Fetching from API..."
    )

    filled_count = 0
    for index, row in tqdm(
        rows_to_update.iterrows(),
        total=len(rows_to_update),
        desc="Fyller populærnavn",
    ):
        taxon_id_val = row[ID_COLUMN]
        print(
            f"DEBUG: Processing row index: {index}, {ID_COLUMN}: {taxon_id_val}"
        )

        try:
            taxon_id_for_api = int(taxon_id_val)
            print(
                f"DEBUG: Successfully converted {ID_COLUMN} '{taxon_id_val}' to int: {taxon_id_for_api}"
            )
        except (ValueError, TypeError) as e:
            print(
                f"DEBUG: Skipping row {index}: Cannot convert ID '{taxon_id_val}' in '{ID_COLUMN}' to int. Error: {e}"
            )
            continue

        taxon_api_data = fetch_taxon_data(taxon_id_for_api)
        if taxon_api_data:
            popular_name = extract_norwegian_popular_name(taxon_api_data)
            if popular_name:
                print(
                    f"DEBUG: Updating row {index} with popular name: '{popular_name}'"
                )
                df.loc[index, POPULAR_NAME_COLUMN] = popular_name
                filled_count += 1
            else:
                print(
                    f"DEBUG: No popular name extracted for row {index}, ID {taxon_id_for_api}."
                )
        else:
            print(
                f"DEBUG: No taxon API data received for row {index}, ID {taxon_id_for_api}."
            )

    print(
        f"DEBUG: fill_missing_popular_names - Successfully filled {filled_count} missing popular names."
    )
    return df


def main(
    input_csv_path: Union[str, Path], output_csv_path: Union[str, Path]
) -> Optional[Path]:
    """Hovedfunksjon for å laste, behandle og lagre data.

    Args:
        input_csv_path: Sti til input CSV-filen.
        output_csv_path: Sti for å lagre den behandlede CSV-filen.

    Returns:
        Stien til outputfilen hvis vellykket, ellers None.
    """
    print(
        f"DEBUG: main called with input: {input_csv_path}, output: {output_csv_path}"
    )
    try:
        input_p = Path(input_csv_path)
        output_p = Path(output_csv_path)

        if not input_p.exists():
            print(f"DEBUG: main - Error: Input file not found at {input_p}")
            return None

        output_p.parent.mkdir(parents=True, exist_ok=True)

        print(f"DEBUG: main - Reading CSV: {input_p}")
        df = pd.read_csv(input_p, low_memory=False, sep=';', quotechar='"', skipinitialspace=True)
        print(f"DEBUG: main - CSV read. DataFrame shape: {df.shape}")
        print(f"DEBUG: main - DataFrame columns: {df.columns.tolist()}")
        print(
            f"DEBUG: main - Example of {ID_COLUMN} before processing:\n{df[ID_COLUMN].head()}"
        )
        print(
            f"DEBUG: main - Example of {POPULAR_NAME_COLUMN} before processing:\n{df[POPULAR_NAME_COLUMN].head()}"
        )

        df_updated = fill_missing_popular_names(df)
        print(f"DEBUG: main - Writing updated CSV to: {output_p}")
        df_updated.to_csv(output_p, index=False, encoding="utf-8")
        print(f"DEBUG: main - Processed file saved to: {output_p}")
        return output_p
    except FileNotFoundError:
        print(f"DEBUG: main - FileNotFoundError for {input_csv_path}")
        return None
    except pd.errors.EmptyDataError:
        print(f"DEBUG: main - EmptyDataError for {input_csv_path}")
        return None
    except Exception as e:
        print(f"DEBUG: main - An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    print("DEBUG: Running manglende_navn.py directly for testing.")

    # Define paths for testing
    # Using the Andøya_fugl.csv file directly as input for this test run.
    workspace_root = Path(
        "/Users/havardhjermstad-sollerud/Documents/Kodeprosjekter/python/streamlit/artsdata-working"
    )
    test_input_file = (
        workspace_root / "databehandling" / "input_artsdata" / "Andøya_fugl.csv"
    )

    # Define a specific output file for this debug run
    debug_output_dir = workspace_root / "databehandling" / "output"
    debug_output_dir.mkdir(
        parents=True, exist_ok=True
    )  # Ensure debug output dir exists
    test_output_file = debug_output_dir / "Andøya_fugl_names_filled_debug.csv"

    print(f"DEBUG: Test input file path: {test_input_file}")
    print(f"DEBUG: Test output file path: {test_output_file}")

    if not test_input_file.exists():
        print(
            f"DEBUG: Test input file {test_input_file} not found. Please ensure the path is correct."
        )
        print("DEBUG: Exiting test run.")
    else:
        print(f"DEBUG: Attempting to process {test_input_file}...")
        result_path = main(test_input_file, test_output_file)
        if result_path:
            print(f"DEBUG: Test completed. Output: {result_path}")
            print(
                f"DEBUG: Please check {test_output_file} and the console logs, especially for entries related to ID 3768."
            )
        else:
            print("DEBUG: Test failed. Check console logs for errors.")

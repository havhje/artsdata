# Artsdata Analysis Streamlit Application

## Overview

This Streamlit application provides an interactive interface for exploring and analyzing species observation data, likely originating from Artsdatabanken or similar sources. It allows users to load data, apply filters, view key statistics and trends on a dashboard, and examine the raw data in organized tables.

## Core Functionality

1.  **Data Loading**:
    *   The application (`Oversikt.py`) attempts to load a pre-processed CSV file (`databehandling/output/Andøya_fugl_taxonomy.csv`) by default.
    *   If the local file is not found, it provides a file uploader for the user to supply their own CSV data.
    *   Loaded data is stored in Streamlit's session state (`st.session_state['loaded_data']`) for use across different pages/modules.

2.  **Filtering**:
    *   A sidebar (`global_utils/filter.py`) allows users to filter the loaded data based on taxonomic ranks (currently Familie, Orden, Art) using multi-select widgets.
    *   Filters are applied dynamically, and the filtered dataset is used for subsequent displays.
    *   **Filter selections persist across different pages** of the application, managed by the session state logic.

3.  **Column Renaming**:
    *   Uses a mapping defined in `global_utils/column_mapping.py` to translate technical data column names into more user-friendly Norwegian names for display in the UI.

4.  **Dashboard (`mapper_streamlit/landingsside/`)**:
    *   Displays a summary dashboard (`mapper_streamlit/landingsside/dashboard.py`) based on the **filtered and renamed** data.
    *   Shows key metrics (total observations, individuals, unique counts).
    *   Calculates and displays statistics related to Red List status, Alien Species status, and other conservation categories.
    *   Presents configurable "Top 10" lists for various categories (species, families, observers, etc.).
    *   Includes an interactive Plotly chart showing yearly trends for observations, individuals, and average individuals per observation, allowing users to toggle traces.

5.  **Main Data Table (`Oversikt.py`)**:
    *   Displays the **filtered** data in a primary table.
    *   Separates observations identified as "Alien Species" based on specific criteria (either a dedicated 'Fremmede arter' column or specific 'category' values like 'SE', 'HI', 'PH', 'LO').
    *   Shows non-alien species in the main table and alien species in a separate table below if any exist.
    *   Applies the user-friendly column names (`global_utils/column_mapping.py`) and attempts to order columns logically for readability.

6.  **Session State Persistence**:
    *   The `global_utils/session_state_manager.py` module ensures that filter values selected by the user are preserved in `st.session_state` even when navigating between different application pages.
    *   It achieves this by initializing necessary keys if they don't exist and preventing Streamlit's default widget state clean-up for these specific keys.

7.  **PDF Vector Search** (`pages/8_KI_vektor_database.py`):
    *   Allows users to perform semantic searches against the content of pre-processed PDF documents stored in a Weaviate vector database.
    *   Connects to a Weaviate Cloud instance using credentials stored in `.streamlit/secrets.toml`.
    *   Uses the Cohere embedding model (via Weaviate integration) to vectorize user queries and find relevant text chunks.
    *   Displays the most relevant text chunks along with their source PDF and page number.

## Structure

*   `Oversikt.py`: The main application script, orchestrating loading, filtering, dashboard display, and table views.
*   `global_utils/`: Contains utility modules shared across the application:
    *   `column_mapping.py`: Defines the mapping from technical to display names.
    *   `filter.py`: Implements the sidebar filter widgets and the logic to apply filters.
    *   `session_state_manager.py`: Handles the initialization and persistence logic for filter values in session state.
    *   `KI_vektor_skript.py`: Standalone script (run manually) responsible for processing PDFs, chunking text, connecting to Weaviate, and ingesting the vectorized data into the `PdfChunks` collection.
*   `mapper_streamlit/landingsside/`: Contains modules specific to the main dashboard view:
    *   `dashboard.py`: Orchestrates the calculation and display of dashboard components.
    *   `utils_dashboard/`: Sub-modules for calculations (basic metrics, status counts, top lists) and UI display logic.
    *   `figures_dashboard/`: Sub-modules for generating the observation period Plotly figure.
*   `pages/`: Contains other Streamlit pages for different views:
    *   `2_Søylediagrammer.py`: Example page (content TBD).
    *   `8_KI_vektor_database.py`: Page providing the user interface for PDF vector search.
*   `databehandling/output/`: Expected location for processed input data (e.g., taxonomy CSV).
*   `vektor_database/`: Directory containing the source PDF files for vector database ingestion.
*   `project.doc.md`: This file, providing an overview of the project.
*   `.env`: Local file (ignored by Git) storing API keys for the standalone ingestion script.
*   `.streamlit/secrets.toml`: Streamlit file storing secrets (API keys, tokens) for the running application.
*   `.streamlit/config.toml`: Streamlit file for non-secret configurations.

## How to Run

1.  **Run Streamlit App:**
    ```bash
    # From the workspace root (artsdata directory)
    uv run streamlit run Oversikt.py
    ```
2.  **Run PDF Ingestion (One-time or when PDFs change):**
    *   Ensure the `.env` file is populated with correct API keys (Weaviate URL/Key, Cohere Key).
    *   Delete the `PdfChunks` collection in your Weaviate Cloud instance if you need a completely clean import.
    ```bash
    # From the workspace root (artsdata directory)
    uv run python global_utils/KI_vektor_skript.py
    ```

## Development Notes & Challenges

*   **PDF Ingestion Script (`KI_vektor_skript.py`):**
    *   **Secrets Handling:** Initial attempts to use `st.secrets` within the standalone ingestion script failed because `st.secrets` is only populated when running via `streamlit run`. Switched to using `python-dotenv` and a `.env` file for managing secrets in the standalone script context.
    *   **Weaviate Client v4 API:** Encountered several `AttributeError` issues due to API changes between Weaviate client v3 and v4, particularly around schema definition (`wvc.config.Property` vs `wvc.Property`) and batch configuration.
    *   **Batching & Rate Limits:** The initial PDF ingestion attempts using Weaviate's dynamic batching (`collection.batch.dynamic()`) failed due to hitting Cohere's free tier API rate limits (specifically `trial token rate limit exceeded`).
    *   **Troubleshooting Batching:** Attempts to fix rate limiting by explicitly configuring smaller batch sizes (`client.batch.configure`, configuring via `ConnectionParams`, configuring via `collection.batch.add`) failed due to `AttributeError`s, indicating difficulties finding the correct v4 syntax for modifying batch behavior post-connection or during connection with `connect_to_wcs`.
    *   **Current Approach:** Reverted to dynamic batching (`collection.batch.dynamic()`) assuming the user has upgraded Cohere capacity. Further refinement might involve implementing manual batching with delays (`time.sleep`) or switching embedding providers if rate limits persist.
*   **Streamlit Weaviate Connection (`pages/8_KI_vektor_database.py`):**
    *   The `streamlit-weaviate` connection helper mentioned in some Streamlit blogs was not found as a standard installable package via `uv add`.
    *   Initial attempts to use `st.connection(..., type=WeaviateConnection)` failed with `ModuleNotFoundError`.
    *   Subsequent attempts to use generic `st.connection(...)` failed with `KeyError: 'connections'` because it expected a specific configuration structure in `secrets.toml`.
    *   **Current Approach:** The Streamlit page now connects to Weaviate *manually* using `weaviate.connect_to_wcs(...)` within the page script, bypassing `st.connection` for this specific integration.

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

## Structure

*   `Oversikt.py`: The main application script, orchestrating loading, filtering, dashboard display, and table views.
*   `global_utils/`: Contains utility modules shared across the application:
    *   `column_mapping.py`: Defines the mapping from technical to display names.
    *   `filter.py`: Implements the sidebar filter widgets and the logic to apply filters.
    *   `session_state_manager.py`: Handles the initialization and persistence logic for filter values in session state.
*   `mapper_streamlit/landingsside/`: Contains modules specific to the main dashboard view:
    *   `dashboard.py`: Orchestrates the calculation and display of dashboard components.
    *   `utils_dashboard/`: Sub-modules for calculations (basic metrics, status counts, top lists) and UI display logic.
    *   `figures_dashboard/`: Sub-modules for generating the observation period Plotly figure.
*   `pages/`: Likely contains other Streamlit pages (e.g., `2_Søylediagrammer.py`), suggesting a multi-page application structure where data loaded in `Oversikt.py` might be used.
*   `databehandling/output/`: Expected location for processed input data.
*   `project.doc.md`: This file, providing an overview of the project.

## How to Run

Assuming dependencies (`streamlit`, `pandas`, `plotly`, `pathlib`) are installed (preferably using `uv sync`):

```bash
# From the workspace root (artsdata directory)
uv run streamlit run Oversikt.py
```

This will start the Streamlit server and open the application in a web browser.

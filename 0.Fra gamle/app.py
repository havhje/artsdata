import streamlit as st
import pandas as pd
from typing import Dict, Optional

from config import PREFERRED_COLUMN_ORDER, CSV_SEPARATOR, CSV_DECIMAL
from models.data_loader import get_available_files, load_data
from models.species_data import SpeciesData
from utils.column_mapping import get_display_name
from utils.error_handling import handle_error

# Set the page layout to wide
st.set_page_config(layout="wide")
st.title("Data Viewer")

# Initialize session state keys if they don't exist
def init_session_state():
    """Initialize session state with default values."""
    defaults = {
        'species_data': SpeciesData(),
        'selected_categories': [],
        'selected_taxon_groups': [],
        'selected_forvaltning': 'Any',  # Options: Any, Yes, No
        'selected_criteria': [],
        'start_date': None,
        'end_date': None,
        'search_term': '',
        'current_file': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

def render_sidebar_filters(
    species_data: SpeciesData
) -> None:
    """
    Render filter widgets in the sidebar.
    
    Args:
        species_data: SpeciesData instance with loaded data
    """
    with st.sidebar:
        st.header("Filters")
        
        # Only show filters if data is loaded
        if species_data.data.empty:
            st.info("Load data using the dropdown above to enable filters.")
            return
        
        # 1. Category Filter
        category_col = 'category'
        if category_col in species_data.data.columns:
            unique_categories = species_data.get_unique_values(category_col)
            st.multiselect(
                get_display_name(category_col),
                options=unique_categories,
                key='selected_categories'
            )
        else:
            st.caption(f"{get_display_name(category_col)} column not found.")
        
        # 2. Taxon Group Filter
        taxon_group_col = 'taxonGroupName'
        if taxon_group_col in species_data.data.columns:
            unique_groups = species_data.get_unique_values(taxon_group_col)
            st.multiselect(
                get_display_name(taxon_group_col),
                options=unique_groups,
                key='selected_taxon_groups'
            )
        else:
            st.caption(f"{get_display_name(taxon_group_col)} column not found.")
        
        # 3. Forvaltningsinteresse Filter
        forvaltning_col = 'is_forvaltningsinteresse'
        if forvaltning_col in species_data.data.columns:
            st.selectbox(
                get_display_name(forvaltning_col),
                options=["Any", "Yes", "No"],
                key='selected_forvaltning'
            )
        else:
            st.caption(f"{get_display_name(forvaltning_col)} column not found.")
        
        # 4. Criteria Filter
        criteria_col = 'forvaltningsinteresse_kriterium'
        if criteria_col in species_data.data.columns:
            # Extract unique individual criteria
            all_criteria_list = (
                species_data.data[criteria_col]
                .dropna()
                .astype(str)
                .str.split(',')
                .explode()
            )
            unique_criteria = sorted(all_criteria_list.str.strip().unique())
            # Remove empty strings
            unique_criteria = [crit for crit in unique_criteria if crit]
            
            if unique_criteria:
                st.multiselect(
                    f"{get_display_name(criteria_col)} (OR selection)",
                    options=unique_criteria,
                    key='selected_criteria'
                )
            else:
                st.caption("No criteria values found.")
        else:
            st.caption(f"{get_display_name(criteria_col)} column not found.")
        
        # 5. Date Range Filter
        date_col = 'dateTimeCollected'
        if date_col in species_data.data.columns:
            try:
                # Convert to datetime for finding min/max
                date_series = pd.to_datetime(
                    species_data.data[date_col], errors='coerce'
                ).dropna()
                
                min_date = date_series.min().date() if not date_series.empty else None
                max_date = date_series.max().date() if not date_series.empty else None
                
                # Use min/max for widgets
                st.date_input(
                    f"Start {get_display_name(date_col)}",
                    value=st.session_state.start_date,
                    min_value=min_date,
                    max_value=max_date,
                    key='start_date'
                )
                st.date_input(
                    f"End {get_display_name(date_col)}",
                    value=st.session_state.end_date,
                    min_value=min_date,
                    max_value=max_date,
                    key='end_date'
                )
            except Exception as e:
                handle_error(e, "Could not create date filters", "app", ui_component=st.warning)
        else:
            st.caption(f"{get_display_name(date_col)} column not found.")
        
        # 6. General Text Search
        st.text_input("Search all text (space = AND)", key='search_term')
        st.caption("Searches across all text fields.")

def render_data_viewer(species_data: SpeciesData) -> None:
    """
    Render the data viewer with filtered data.
    
    Args:
        species_data: SpeciesData instance with data to display
    """
    # Apply filters
    filtered_data = species_data.filter_data(
        selected_categories=st.session_state.selected_categories,
        selected_taxon_groups=st.session_state.selected_taxon_groups,
        selected_forvaltning=st.session_state.selected_forvaltning,
        selected_criteria=st.session_state.selected_criteria,
        start_date=st.session_state.start_date,
        end_date=st.session_state.end_date,
        search_term=st.session_state.search_term
    )
    
    # Display filtered data
    if not filtered_data.empty:
        # Prepare data for display with proper column order and names
        display_data = species_data.prepare_display_data()
        
        # Display dataframe
        st.dataframe(display_data, use_container_width=True, height=600)
        st.write(f"Showing {len(filtered_data)} matching records.")
        
        # Display map
        render_map(species_data)
    else:
        st.warning("No records match the current filter criteria.")

def render_map(species_data: SpeciesData) -> None:
    """
    Render a map with the filtered data points.
    
    Args:
        species_data: SpeciesData instance with filtered data
    """
    st.subheader("Map of Filtered Observations")
    
    # Get map data
    map_data = species_data.get_map_data()
    
    if map_data is not None:
        st.map(map_data)
    else:
        # Find coordinate column names for better error message
        lat_cols = ['decimalLatitude', 'latitude', 'lat']
        lon_cols = ['decimalLongitude', 'longitude', 'lon']
        
        lat_display = next((get_display_name(col) for col in lat_cols 
                           if col in species_data.filtered_data.columns), None)
        lon_display = next((get_display_name(col) for col in lon_cols 
                           if col in species_data.filtered_data.columns), None)
        
        if lat_display and lon_display:
            st.info("No valid coordinates found in the filtered data.")
        else:
            st.warning(
                "Could not find standard coordinate columns (e.g., "
                f"{get_display_name('decimalLatitude')}/"
                f"{get_display_name('decimalLongitude')}) in the data."
            )

def render_file_selector() -> Optional[str]:
    """
    Render the file selector and handle file selection.
    
    Returns:
        Selected filename or None if no file selected
    """
    # Get available files
    available_files, available_filenames = get_available_files()
    
    if not available_filenames:
        st.warning(f"No processed files ('*_forvaltning.csv') found.")
        st.session_state.species_data = SpeciesData()
        st.session_state.current_file = None
        return None
    
    # File selector
    st.subheader("Select Processed File")
    selected_filename = st.selectbox(
        "Choose a file to view:",
        available_filenames,
        index=None,
        placeholder="Select a file...",
        key='selectbox_file'
    )
    
    # Check if file selection changed
    file_changed = selected_filename != st.session_state.get('current_file')
    
    if selected_filename and file_changed:
        # Find the selected file path
        selected_filepath = next(
            (f for f in available_files if f.name == selected_filename), 
            None
        )
        
        if selected_filepath:
            st.write(f"Loading data from: `{selected_filepath}`")
            
            # Load the data
            df_loaded = load_data(selected_filepath)
            
            if df_loaded is not None:
                # Update session state
                st.session_state.species_data = SpeciesData(df_loaded)
                st.session_state.current_file = selected_filename
                
                # Reset filters
                st.session_state.selected_categories = []
                st.session_state.selected_taxon_groups = []
                st.session_state.selected_forvaltning = 'Any'
                st.session_state.selected_criteria = []
                st.session_state.start_date = None
                st.session_state.end_date = None
                st.session_state.search_term = ''
                
                st.success(f"Loaded {len(df_loaded)} rows from {selected_filename}")
    
    return selected_filename

def main() -> None:
    """Main application flow."""
    # Initialize session state
    init_session_state()
    
    # Render file selector
    selected_filename = render_file_selector()
    
    # Get species data from session state
    species_data = st.session_state.get('species_data', SpeciesData())
    
    # Render sidebar filters
    render_sidebar_filters(species_data)
    
    # Render data viewer if data is loaded
    if selected_filename or not species_data.data.empty:
        render_data_viewer(species_data)
    elif not selected_filename:
        st.info("Select a file from the dropdown above to display its contents.")

if __name__ == "__main__":
    main()



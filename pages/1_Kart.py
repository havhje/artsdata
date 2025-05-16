import streamlit as st
from global_utils.column_mapping import get_display_name  # Used for mapping original column names to display names.
from global_utils.filtering.filter_ui import display_filter_widgets
from global_utils.filtering.filter_logic import apply_filters
from global_utils.session_state_manager import initialize_and_persist_filters
from global_utils.data_loading import load_and_prepare_data  # Imports the new centralized data loading function.
from global_utils.filtering.filter_constants import ALIEN_CODES  # Imports constants for alien species filtering.
from mapper_streamlit.Kart.figur_1_kart_punkter import punktkart

# ----------------------------------------
# "Prepp"
# ----------------------------------------
# Bruker riktig navn
display_name = get_display_name("preferredPopularName")

# Henter data fra session state
innlastet_data = st.session_state.get("loaded_data")

# Initialize/Persist Session State
initialize_and_persist_filters()

# Display Filter Widgets in Sidebar
display_filter_widgets(innlastet_data)  # Displays filter widgets

# Henter filtrerte data fra session state
kart_data_filtrert = apply_filters(innlastet_data)

# ----------------------------------------
# Kart med punkter
# ----------------------------------------
st.title("Kart")
options = ["Art", "Familie"]
color_by = selection = st.pills("Farge etter", options, default="Art", selection_mode="single")
st.plotly_chart(punktkart(kart_data_filtrert, color_by))

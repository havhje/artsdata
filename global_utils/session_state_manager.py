##### Imports #####
import streamlit as st # Import Streamlit for session state access

##### Constants #####
# List of session state keys used by filters that need to persist across pages
PERSISTENT_FILTER_KEYS = [
    'filter_familie',              # Key for the Familie filter
    'filter_orden',                # Key for the Orden filter
    'filter_art',                  # Key for the Art filter
    'filter_redlist_category',     # Key for the Red List category filter
    'filter_special_category',     # Key for the Special category filter
    'filter_alien_category',       # Key for the Alien species category filter
    'filter_start_date',           # Key for the Start Date filter
    'filter_end_date',             # Key for the End Date filter
    'filter_general_text'          # Key for the General text search filter
    # Add future filter keys here
]

##### Functions #####

# --- Function: initialize_and_persist_filters ---
# Ensures filter keys exist in session state and prevents their deletion during widget cleanup.
# Call this function at the beginning of each Streamlit page script.
def initialize_and_persist_filters():
    # Iterate through the defined list of keys that should persist
    for key in PERSISTENT_FILTER_KEYS: # Loop through each specified filter key
        # Initialize the key with a default value if it doesn't exist
        if key not in st.session_state:
            if key == 'filter_general_text':
                st.session_state[key] = "" # Default text search to empty string
            elif key == 'filter_start_date' or key == 'filter_end_date':
                st.session_state[key] = None # Default dates to None initially
            else:
                st.session_state[key] = [] # Default multiselects to empty list

        # --- Interrupt Widget Clean-up ---
        # Re-assign the key to itself to prevent cleanup.
        st.session_state[key] = st.session_state[key] # Re-assignment prevents cleanup

# --- Optional: Add other session state management functions here if needed --- 
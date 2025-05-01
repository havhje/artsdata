##### Imports #####
import streamlit as st # Import Streamlit for session state access

##### Constants #####
# List of session state keys used by filters that need to persist across pages
PERSISTENT_FILTER_KEYS = [
    'filter_familie', # Key for the Familie filter
    'filter_orden',   # Key for the Orden filter
    'filter_art'      # Key for the Art filter
    # Add future filter keys here
]

##### Functions #####

# --- Function: initialize_and_persist_filters ---
# Ensures filter keys exist in session state and prevents their deletion during widget cleanup.
# Call this function at the beginning of each Streamlit page script.
def initialize_and_persist_filters():
    # Iterate through the defined list of keys that should persist
    for key in PERSISTENT_FILTER_KEYS: # Loop through each specified filter key
        # Initialize the key with a default empty list if it doesn't exist
        if key not in st.session_state: # Check if the key is absent from session state
            st.session_state[key] = [] # Assign an empty list as the default value

        # --- Interrupt Widget Clean-up ---
        # Re-assign the key to itself. This detaches it from the widget lifecycle
        # for the purpose of cleanup, ensuring it persists even if the filter
        # widget is not rendered on the current page.
        st.session_state[key] = st.session_state[key] # Re-assignment prevents cleanup

# --- Optional: Add other session state management functions here if needed --- 
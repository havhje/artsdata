##### Imports #####
import streamlit as st # Import the Streamlit library
from global_utils.filter import display_filter_widgets, apply_filters
import pandas as pd # Import pandas for creating empty DataFrame

# --- Attempt to retrieve data from session state ---
kart_data = pd.DataFrame() # Initialize as empty DataFrame
if 'loaded_data' in st.session_state: # Check if the key exists BEFORE accessing it
    kart_data = st.session_state['loaded_data'] # Access data only if it exists
else:
    st.warning("Data ikke lastet inn. Gå til Oversikt-siden og last inn data først.") # Show warning if data not found

##### Main Page Content #####
st.title("Kart") # Set the title of the page
st.write("Innhold for Kart-siden kommer her.") # Add some placeholder text

# --- Display Filters (if data is available) ---

display_filter_widgets(kart_data) # Call the function to show sidebar filters
filtered_kart_data = apply_filters(kart_data) # Apply the filters
    # Now you can use filtered_kart_data to display maps, charts etc.
st.dataframe(filtered_kart_data) # Display the entire filtered DataFrame


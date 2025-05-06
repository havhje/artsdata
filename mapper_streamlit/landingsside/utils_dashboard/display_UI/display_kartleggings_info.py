# ##### Imports #####
import streamlit as st # Import Streamlit for UI elements.
import pandas as pd # Import pandas (though mainly used by formatters passed in).

# ##### Display Functions #####

# --- Function: display_main_metrics_grid ---
# Displays the main 5-column grid with basic metrics and their conditional top lists.
# Takes metrics dict, top_lists dict, show_top_lists bool, and formatters dict.
def display_main_metrics_grid(metrics, top_lists, show_top_lists, formatters):
    # --- Main Metrics Grid ---
    col1, col2, col3, col4, col5 = st.columns(5) # Use 5 columns for the main stats.

    # Unpack formatters for easier access
    format_freq = formatters['format_top_frequency_md']
    format_obs = formatters['format_top_observations_md']

    with col1:  # Content for the first column (Total Observations).
        st.metric(label="Totalt Antall Observasjoner", value=f"{metrics['total_records']:,}".replace(',', ' ')) # Display total records with formatting.
        # Conditionally display the Top 10 Species list (Frequency only)
        if show_top_lists:
            # Use the frequency formatter with the appropriate DataFrame and columns.
            st.markdown(format_freq(top_lists['top_species_freq'], title="", item_col='Art', count_col='Antall Observasjoner'))

    with col2: # Content for the second column (Total Individuals).
        st.metric(label="Totalt Antall Individer", value=f"{metrics['total_individuals']:,}".replace(',', ' ')) # Display total individuals sum with formatting.
        # Conditionally display Top 10 Observations by Individual Count
        if show_top_lists:
            # Use the specific observation formatter.
            st.markdown(format_obs(top_lists['top_individual_obs'])) # Call the formatter

    with col3: # Content for the third column (Unique Species).
        st.metric(label="Unike Arter", value=f"{metrics['unique_species']:,}".replace(',', ' ')) # Display unique species count.
        # No top list associated directly here in the original layout.

    with col4: # Content for the fourth column (Unique Families).
        st.metric(label="Unike Familier", value=f"{metrics['unique_families']:,}".replace(',', ' ')) # Display unique family count.
        # Conditionally display the Top 10 Families list (Frequency only)
        if show_top_lists:
             # Use the frequency formatter with the appropriate DataFrame and columns.
             st.markdown(format_freq(top_lists['top_families_freq'], title="", item_col='Familie', count_col='Antall Observasjoner'))

    with col5: # Content for the fifth column (Unique Observers).
        st.metric(label="Unike Innsamlere/Observatører", value=f"{metrics['unique_observers']:,}".replace(',', ' ')) # Display unique observer count.
        # Conditionally display the Top 10 Observers list (Frequency only)
        if show_top_lists:
            # Use the frequency formatter with the appropriate DataFrame and columns.
            st.markdown(format_freq(top_lists['top_observers_freq'], title="", item_col='Innsamler/Observatør', count_col='Antall Observasjoner'))

with col1:  # Content for the first column (Total Observations).
    st.metric(label="Totalt Antall Observasjoner", value=f"{metrics['total_records']:,}".replace(',', ' ')) # Display total records with formatting.
    # Conditionally display the Top 10 Species list (Frequency only)
    if show_top_lists:
        # Use the frequency formatter with the appropriate DataFrame and columns.
        st.markdown(format_freq(top_lists['top_species_freq'], title="", item_col='Art', count_col='Antall_Observasjoner'), unsafe_allow_html=True)

with col2: # Content for the second column (Total Individuals).
    st.metric(label="Totalt Antall Individer", value=f"{metrics['total_individuals']:,}".replace(',', ' ')) # Display total individuals sum with formatting.
    # Conditionally display Top 10 Observations by Individual Count
    if show_top_lists:
        # Use the specific observation formatter.
        st.markdown(format_obs(top_lists['top_individual_obs']), unsafe_allow_html=True) # Call the formatter

with col3: # Content for the third column (Unique Species).
    st.metric(label="Unike Art", value=f"{metrics['unique_species']:,}".replace(',', ' ')) # Display unique species count.
    # Conditionally display the Top 10 Species list (Frequency only)
    if show_top_lists:
        # Use the frequency formatter with the appropriate DataFrame and columns.
        st.markdown(format_freq(top_lists['top_species_freq'], title="", item_col='Art', count_col='Antall_Observasjoner'), unsafe_allow_html=True)

with col4: # Content for the fourth column (Unique Families).
    st.metric(label="Unike Familier", value=f"{metrics['unique_families']:,}".replace(',', ' ')) # Display unique family count.
    # Conditionally display the Top 10 Families list (Frequency only)
    if show_top_lists:
        # Use the frequency formatter with the appropriate DataFrame and columns.
        st.markdown(format_freq(top_lists['top_families_freq'], title="", item_col='Familie', count_col='Antall_Observasjoner'), unsafe_allow_html=True)

with col5: # Content for the fifth column (Unique Observers).
    st.metric(label="Unike Innsamlere/Observatører", value=f"{metrics['unique_observers']:,}".replace(',', ' ')) # Display unique observer count.
    # Conditionally display the Top 10 Observers list (Frequency only)
    if show_top_lists:
        # Use the frequency formatter with the appropriate DataFrame and columns.
        st.markdown(format_freq(top_lists['top_observers_freq'], title="", item_col='Innsamler/Observatør', count_col='Antall Observasjoner'), unsafe_allow_html=True) 
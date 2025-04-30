# ##### Imports #####
import streamlit as st
import pandas as pd
# from global_utils.column_mapping import get_display_name # Removed, assuming data arrives renamed


##### Functions #####

# --- Helper Function: format_top_observations_md ---
# Formats a DataFrame of top observations into a markdown list.
# Assumes df has columns 'Antall Individer' and 'Art'.
def format_top_observations_md(df):
    md_string = "" # Initialize empty string.
    if df.empty:
        return "_Ingen observasjoner å vise._" # Return message if DataFrame is empty.
    # Ensure 'Antall Individer' is integer for display
    df['Antall Individer'] = pd.to_numeric(df['Antall Individer'], errors='coerce').fillna(0).astype(int)
    # Use enumerate to get a counter starting from 0 for correct list numbering (1-based)
    for i, (_, row) in enumerate(df.iterrows()): # Use enumerate for 1-based numbering
        # Format: "1. Count Art". Add newline.
        md_string += f"{i + 1}. {row['Antall Individer']:,} {row['Art']}\n" # Use counter i+1
    return md_string # Return the formatted markdown string.


# --- Function: display_dashboard ---
# Displays key metrics and top 10 lists based on the input data.
# Assumes 'data' is a pandas DataFrame with Norwegian column names.
def display_dashboard(data):
    # --- Initialize Session State for Top 10 Visibility ---
    # Ensures state persists across reruns for toggling lists.
    if 'show_dashboard_top_lists' not in st.session_state:
        st.session_state.show_dashboard_top_lists = False # Default: hide all top lists

    # --- Empty Data Check ---
    if data.empty:  # Checks if the DataFrame is empty after filtering.
        st.warning("Ingen data matcher de valgte filtrene.")  # Display warning if no data.
        return  # Stop execution if no data.

    # --- Calculate Metrics ---
    # Basic Counts & Sums
    total_records = len(data)  # Get total number of observations. Filter changes affect this.
    # Sum individuals, coercing errors to 0. Safer than direct sum.
    total_individuals = pd.to_numeric(data["Antall Individer"], errors='coerce').fillna(0).astype(int).sum()
    unique_species = data["Art"].nunique()  # Count unique species names.
    unique_families = data["Familie"].nunique()  # Count unique family names.
    unique_observers = data["Innsamler/Observatør"].nunique()  # Re-enabled calculation for display.

    # Date Range
    # Convert to datetime, coercing errors to NaT (Not a Time).
    valid_dates = pd.to_datetime(data["Innsamlingsdato/-tid"], errors='coerce').dropna()
    min_date = valid_dates.min() if not valid_dates.empty else None  # Get earliest date if available.
    max_date = valid_dates.max() if not valid_dates.empty else None  # Get latest date if available.

    # Status Counts (Redlist, Alien, Priority etc.)
    # Assumes standard category codes exist in the renamed columns.
    redlist_categories = ['CR', 'EN', 'VU', 'NT', 'DD']  # Define redlist categories. Modifying affects count.
    # Count rows matching redlist categories (Total).
    redlisted_total_count = data["Kategori (Rødliste/Fremmedart)"].isin(redlist_categories).sum()

    # --- Calculate Individual Red List Category Counts ---
    # Calculate count for each specific red list category.
    redlist_counts_individual = {} # Initialize dictionary to store counts per category.
    for category in redlist_categories: # Iterate through the defined categories.
        # Count rows where the category column exactly matches the current category.
        redlist_counts_individual[category] = (data["Kategori (Rødliste/Fremmedart)"] == category).sum()

    # --- Calculate Alien Species Counts (Total and Breakdown) ---
    alien_categories_list = ['SE', 'HI', 'PH', 'LO']  # Define specific alien risk categories.
    alien_yes_col = "Fremmede arter kategori" # Define the dedicated 'Yes' column name.
    category_col = "Kategori (Rødliste/Fremmedart)" # Define the category column name.

    is_alien_category = data[category_col].isin(alien_categories_list)  # Check category column.
    is_alien_yes = data[alien_yes_col] == 'Yes'  # Check dedicated 'Yes' column.
    alien_count = (is_alien_category | is_alien_yes).sum()  # Total alien count.

    # Calculate counts for each breakdown category
    alien_counts_individual = {} # Dictionary to store breakdown counts.
    for category in alien_categories_list: # Iterate through risk categories.
        alien_counts_individual[category] = (data[category_col] == category).sum() # Count matches in category column.

    # --- Calculate Other Status Counts ---
    prioriterte_count = (data["Prioriterte Arter"] == 'Yes').sum()  # Count 'Yes' in Prioriterte Arter.
    andre_spes_hensyn_count = (data["Andre Spes. Hensyn."] == 'Yes').sum()  # Count 'Yes' in Andre Spes. Hensyn.
    ansvarsarter_count = (data["Ansvarsarter"] == 'Yes').sum()  # Count 'Yes' in Ansvarsarter.
    spes_okol_former_count = (data["Spes. Økol. Former"] == 'Yes').sum()  # Count 'Yes' in Spes. Økol. Former.

    # --- Calculate Total for Special Status ---
    # Sum the individual 'Yes' counts for the title display.
    total_special_status_count = (
        prioriterte_count + andre_spes_hensyn_count + ansvarsarter_count + spes_okol_former_count
    )

    # --- Calculate Top 10 Lists (Frequency & Individuals) ---
    top_n = 10  # Number of top items to calculate.

    # Top by Frequency (Species, Family, Observer)
    top_species = data["Art"].value_counts().nlargest(top_n).reset_index()
    top_species.columns = ["Art", "Antall Observasjoner"]  # Set display column names.
    top_families = data["Familie"].value_counts().nlargest(top_n).reset_index()
    top_families.columns = ["Familie", "Antall Observasjoner"]  # Set display column names.
    top_observers = data["Innsamler/Observatør"].value_counts().nlargest(top_n).reset_index()
    top_observers.columns = ["Innsamler/Observatør", "Antall Observasjoner"]  # Set display column names.

    # Top by Individual Count (Overall, Redlist, Alien, Special Status)
    # Ensure 'Antall Individer' is numeric for sorting
    data['Antall Individer Num'] = pd.to_numeric(data['Antall Individer'], errors='coerce').fillna(0)

    # Overall Top 10 Observations by Individual Count
    top_individual_obs = data.nlargest(top_n, 'Antall Individer Num')

    # Top 10 Redlisted Observations by Individual Count
    redlisted_data = data[data[category_col].isin(redlist_categories)]
    top_redlist_obs = redlisted_data.nlargest(top_n, 'Antall Individer Num')

    # Top 10 Alien Observations by Individual Count
    alien_criteria = (data[category_col].isin(alien_categories_list)) | (data[alien_yes_col] == 'Yes')
    alien_data = data[alien_criteria]
    top_alien_obs = alien_data.nlargest(top_n, 'Antall Individer Num')

    # Top 10 Special Status Observations by Individual Count
    special_status_cols = ["Prioriterte Arter", "Andre Spes. Hensyn.", "Ansvarsarter", "Spes. Økol. Former"]
    special_criteria = data[special_status_cols].eq('Yes').any(axis=1)
    special_data = data[special_criteria]
    top_special_obs = special_data.nlargest(top_n, 'Antall Individer Num')

    # --- Display Section ---
    # Header and main toggle button side-by-side
    header_cols = st.columns([0.8, 0.2]) # Allocate space: 80% for header, 20% for button
    with header_cols[0]:
        st.subheader("Dashboard Oversikt")  # Add a subheader for the dashboard section.
    with header_cols[1]:
        # Button to toggle all Top 10 lists in this section.
        if st.button("Topp 10", key="toggle_all_lists"):
             st.session_state.show_dashboard_top_lists = not st.session_state.show_dashboard_top_lists # Toggle state.

    # --- Main Metrics Grid ---
    # Use 5 columns
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:  # Content for the first column.
        st.metric(label="Totalt Antall Observasjoner", value=f"{total_records:,}")  # Display total records with formatting.
        # Conditionally display the Top 10 Species list (moved here)
        if st.session_state.show_dashboard_top_lists:
            species_list_md = "" # Initialize empty markdown string.
            # Iterate through the top species DataFrame to build the list.
            for index, row in top_species.iterrows():
                # Format: "1. Count Species Name". Add newline.
                species_list_md += f"{index + 1}. {row['Antall Observasjoner']} {row['Art']}\n"
            st.markdown("**Topp 10 Arter (Hyppighet):**") # Updated title
            st.markdown(species_list_md) # Display the markdown list.
    with col2: # Content for the second column.
        st.metric(label="Totalt Antall Individer", value=f"{total_individuals:,}")  # Display total individuals sum with formatting.
        # Conditionally display Top 10 Observations by Individual Count
        if st.session_state.show_dashboard_top_lists:
            st.markdown("**Topp 10 Observasjoner (Individer):**") # Add title
            st.markdown(format_top_observations_md(top_individual_obs))
    with col3: # Content for the third column.
        st.metric(label="Unike Arter", value=f"{unique_species:,}")  # Display unique species count.
    with col4: # Content for the fourth column.
        st.metric(label="Unike Familier", value=f"{unique_families:,}")  # Display unique family count.
        # Conditionally display the formatted list based on the single session state flag.
        if st.session_state.show_dashboard_top_lists:
            families_list_md = "" # Initialize empty markdown string.
            for index, row in top_families.iterrows():
                 # Format: "1. Count Family Name". Add newline.
                families_list_md += f"{index + 1}. {row['Antall Observasjoner']} {row['Familie']}\n"
            st.markdown("**Topp 10 Familier (Hyppighet):**") # Updated title
            st.markdown(families_list_md) # Display the markdown list.
    with col5: # Content for the fifth column.
        st.metric(label="Unike Innsamlere/Observatører", value=f"{unique_observers:,}") # Display unique observer count here.
        # Conditionally display the formatted list based on the single session state flag.
        if st.session_state.show_dashboard_top_lists:
            observers_list_md = "" # Initialize empty markdown string.
            for index, row in top_observers.iterrows():
                 # Format: "1. Count Observer Name". Add newline.
                observers_list_md += f"{index + 1}. {row['Antall Observasjoner']} {row['Innsamler/Observatør']}\n"
            st.markdown("**Topp 10 Innsamlere (Hyppighet):**") # Updated title
            st.markdown(observers_list_md) # Display the markdown list.


    # --- Individual Red List Category Counts ---
    # st.divider() # Removed divider
    # Section title using markdown, including the total count
    st.markdown(f"#### Antall Funn per Rødlistekategori (Totalt: {redlisted_total_count:,})")
    rl_cols = st.columns(len(redlist_categories)) # Create columns for each category (Should be 5)
    for i, category in enumerate(redlist_categories): # Iterate through categories and columns
        with rl_cols[i]: # Select the appropriate column
            # Display metric for the specific category count.
            st.metric(label=f"Antall {category}", value=f"{redlist_counts_individual[category]:,}")
    # Conditionally display Top 10 Redlisted Observations by Individual Count
    if st.session_state.show_dashboard_top_lists:
        st.markdown("**Topp 10 Rødlistede Observasjoner (Individer):**") # Add title
        st.markdown(format_top_observations_md(top_redlist_obs))

    # --- Individual Alien Species Category Counts ---
    st.markdown(f"#### Antall Funn per Fremmedartkategori (Totalt: {alien_count:,})") # Title with total alien count
    # Display only the risk categories (SE, HI, PH, LO)
    alien_breakdown_categories = alien_categories_list # Use the list of risk categories directly
    # Use 5 columns for alignment, categories will fill first 4
    fa_cols = st.columns(5)
    for i, category in enumerate(alien_breakdown_categories): # Iterate through the 4 categories
        with fa_cols[i]: # Place in columns 0, 1, 2, 3
            count = alien_counts_individual.get(category, 0) # Get count, default to 0 if somehow missing
            label = f"Antall {category}" # Create label
            st.metric(label=label, value=f"{count:,}") # Display metric
    # Conditionally display Top 10 Alien Observations by Individual Count
    if st.session_state.show_dashboard_top_lists:
        st.markdown("**Topp 10 Fremmedart Observasjoner (Individer):**") # Add title
        st.markdown(format_top_observations_md(top_alien_obs))

    # --- Special Status Counts ---
    # st.divider()  # Removed divider
    # Section title using markdown, including the calculated total count
    st.markdown(f"#### Spesielle Status Markeringer (Totalt Antall 'Yes': {total_special_status_count:,})")
    # Use 5 columns for alignment
    spec_col1, spec_col2, spec_col3, spec_col4, spec_col5 = st.columns(5)
    with spec_col1:
        st.metric(label="Prioriterte Arter", value=f"{prioriterte_count:,}")  # Display count for Prioriterte Arter.
    with spec_col2:
        st.metric(label="Andre Spes. Hensyn", value=f"{andre_spes_hensyn_count:,}")  # Display count for Andre Spes. Hensyn.
    with spec_col3:
        st.metric(label="Ansvarsarter", value=f"{ansvarsarter_count:,}")  # Display count for Ansvarsarter.
    with spec_col4:
        st.metric(label="Spes. Økol. Former", value=f"{spes_okol_former_count:,}")  # Display count for Spes. Økol. Former.
    # spec_col5 remains empty
    # Conditionally display Top 10 Special Status Observations by Individual Count
    if st.session_state.show_dashboard_top_lists:
        st.markdown("**Topp 10 Spes. Status Observasjoner (Individer):**") # Add title
        st.markdown(format_top_observations_md(top_special_obs))

    # --- Observation Period ---
    # st.divider()  # Removed divider
    st.markdown("#### Observasjonsperiode")  # Section title using markdown
    # Use 5 columns for alignment, dates in first 2
    date_col1, date_col2, _, _, _ = st.columns(5)
    with date_col1:
        # Format min date or show message.
        min_date_str = min_date.strftime('%Y-%m-%d') if min_date else "Ingen gyldig dato funnet"
        st.metric(label="Første Observasjonsdato", value=min_date_str)  # Display the earliest date found.
    with date_col2:
        # Format max date or show message.
        max_date_str = max_date.strftime('%Y-%m-%d') if max_date else "Ingen gyldig dato funnet"
        st.metric(label="Siste Observasjonsdato", value=max_date_str)  # Display the latest date found.

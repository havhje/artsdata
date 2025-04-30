# ##### Imports #####
import streamlit as st
import pandas as pd
# from global_utils.column_mapping import get_display_name # Removed, assuming data arrives renamed


##### Functions #####


# --- Function: display_dashboard ---
# Displays key metrics and top 5 lists based on the input data.
# Assumes 'data' is a pandas DataFrame with Norwegian column names.
def display_dashboard(data):
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
    unique_observers = data["Innsamler/Observatør"].nunique()  # Count unique observers.

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

    alien_categories = ['SE', 'HI', 'PH', 'LO']  # Define specific alien risk categories.
    is_alien_category = data["Kategori (Rødliste/Fremmedart)"].isin(alien_categories)  # Check category column.
    is_alien_yes = data["Fremmede arter kategori"] == 'Yes'  # Check dedicated 'Yes' column.
    alien_count = (is_alien_category | is_alien_yes).sum()  # Count if either condition is true.

    prioriterte_count = (data["Prioriterte Arter"] == 'Yes').sum()  # Count 'Yes' in Prioriterte Arter.
    andre_spes_hensyn_count = (data["Andre Spes. Hensyn."] == 'Yes').sum()  # Count 'Yes' in Andre Spes. Hensyn.
    ansvarsarter_count = (data["Ansvarsarter"] == 'Yes').sum()  # Count 'Yes' in Ansvarsarter.
    spes_okol_former_count = (data["Spes. Økol. Former"] == 'Yes').sum()  # Count 'Yes' in Spes. Økol. Former.

    # --- Calculate Top 5 Lists (Removed from Display) ---
    # Kept calculation logic in case needed later, but display is removed.
    top_n = 5  # Number of top items.
    # Calculate and rename columns for display clarity.
    top_species = data["Art"].value_counts().nlargest(top_n).reset_index()
    top_species.columns = ["Art", "Antall Observasjoner"]  # Set display column names.

    top_families = data["Familie"].value_counts().nlargest(top_n).reset_index()
    top_families.columns = ["Familie", "Antall Observasjoner"]  # Set display column names.

    top_observers = data["Innsamler/Observatør"].value_counts().nlargest(top_n).reset_index()
    top_observers.columns = ["Innsamler/Observatør", "Antall Observasjoner"]  # Set display column names.

    # --- Display Section ---
    st.subheader("Dashboard Oversikt")  # Add a subheader for the dashboard section.

    # --- Main Metrics Grid ---
    col1, col2, col3 = st.columns(3)  # Creates 3 columns. Adjust number for different layouts.

    with col1:  # Content for the first column.
        st.metric(label="Totalt Antall Observasjoner", value=f"{total_records:,}")  # Display total records with formatting.
        st.metric(label="Totalt Antall Individer", value=f"{total_individuals:,}")  # Display total individuals sum with formatting.
        # Display TOTAL redlisted count. Category list defined above.
        st.metric(label="Totalt Antall Rødlistede Funn (CR-DD)", value=f"{redlisted_total_count:,}") # Updated label slightly

    with col2:  # Content for the second column.
        st.metric(label="Unike Arter", value=f"{unique_species:,}")  # Display unique species count.
        # --- Expander Removed ---
        # with st.expander(f"Topp {top_n} Arter"):  # Creates an expandable section below the metric.
        #     # Display top species table within expander.
        #     st.dataframe(top_species, use_container_width=True, hide_index=True)

        # Display alien species count. Logic defined above.
        st.metric(label="Antall Fremmedart Funn (Risiko/Kat=Yes)", value=f"{alien_count:,}")

    with col3:  # Content for the third column.
        st.metric(label="Unike Familier", value=f"{unique_families:,}")  # Display unique family count.
        # --- Expander Removed ---
        # with st.expander(f"Topp {top_n} Familier"):  # Expandable section for top families.
        #     st.dataframe(top_families, use_container_width=True, hide_index=True)  # Display top families table.

        st.metric(label="Unike Innsamlere/Observatører", value=f"{unique_observers:,}")  # Display unique observer count.
        # --- Expander Removed ---
        # with st.expander(f"Topp {top_n} Innsamlere/Observatører"):  # Expandable section for top observers.
        #     # Display top observers table.
        #     st.dataframe(top_observers, use_container_width=True, hide_index=True)

    # --- Individual Red List Category Counts ---
    st.divider() # Add separator
    st.write("**Antall Funn per Rødlistekategori**") # Section title
    rl_cols = st.columns(len(redlist_categories)) # Create columns for each category
    for i, category in enumerate(redlist_categories): # Iterate through categories and columns
        with rl_cols[i]: # Select the appropriate column
            # Display metric for the specific category count.
            st.metric(label=f"Antall {category}", value=f"{redlist_counts_individual[category]:,}")

    # --- Special Status Counts ---
    st.divider()  # Adds a visual separator line.
    st.write("**Spesielle Status Markeringer (Antall 'Yes')**")  # Add a title for this section.
    col_prio, col_hensyn, col_ansvar, col_okol = st.columns(4)  # Create 4 columns for status counts.
    with col_prio:
        st.metric(label="Prioriterte Arter", value=f"{prioriterte_count:,}")  # Display count for Prioriterte Arter.
    with col_hensyn:
        st.metric(label="Andre Spes. Hensyn", value=f"{andre_spes_hensyn_count:,}")  # Display count for Andre Spes. Hensyn.
    with col_ansvar:
        st.metric(label="Ansvarsarter", value=f"{ansvarsarter_count:,}")  # Display count for Ansvarsarter.
    with col_okol:
        st.metric(label="Spes. Økol. Former", value=f"{spes_okol_former_count:,}")  # Display count for Spes. Økol. Former.

    # --- Observation Period ---
    st.divider()  # Adds another visual separator.
    st.write("**Observasjonsperiode**")  # Add a title for the time period section.
    # Display min/max dates. Handle cases where dates might be None.
    date_col1, date_col2 = st.columns(2)  # Create two columns for dates.
    with date_col1:
        # Format min date or show message.
        min_date_str = min_date.strftime('%Y-%m-%d') if min_date else "Ingen gyldig dato funnet"
        st.metric(label="Første Observasjonsdato", value=min_date_str)  # Display the earliest date found.
    with date_col2:
        # Format max date or show message.
        max_date_str = max_date.strftime('%Y-%m-%d') if max_date else "Ingen gyldig dato funnet"
        st.metric(label="Siste Observasjonsdato", value=max_date_str)  # Display the latest date found.

# ##### Imports #####
import streamlit as st
import pandas as pd
# from global_utils.column_mapping import get_display_name # Removed, assuming data arrives renamed


##### Functions #####

# --- Helper Function: format_top_observations_md --- (Re-added)
# Formats a DataFrame of top observations (by individual count) into a markdown list.
# Assumes df has columns 'Antall Individer' and 'Art'.
def format_top_observations_md(df):
    md_string = "" # Initialize empty string.
    if df.empty:
        return "_Ingen observasjoner å vise._" # Return message if DataFrame is empty.
    # Ensure 'Antall Individer' is integer for display (using the numeric column)
    df_display = df.copy()
    df_display['Antall Individer Display'] = pd.to_numeric(df_display['Antall Individer Num'], errors='coerce').fillna(0).astype(int)
    # Use enumerate to get a counter starting from 0 for correct list numbering (1-based)
    for i, (_, row) in enumerate(df_display.iterrows()): # Use enumerate for 1-based numbering
        # Format: "1. Count Art". Add newline. Use replace for thousands.
        # Pre-format the count number with spaces as thousand separators
        formatted_count = f'{row["Antall Individer Display"]:,}'.replace(',', ' ')
        md_string += f"{i + 1}. {formatted_count} {row['Art']}\n"
    return md_string # Return the formatted markdown string.

# --- Helper Function: format_top_agg_md ---
# Formats a DataFrame (result of groupby().agg()) into a numbered markdown list.
# Shows item name, frequency count, and sum of individuals.
def format_top_agg_md(df, title, item_col, count_col, sum_col):
    md_string = f"**{title}**\n" # Start with the title.
    if df.empty:
        # Append message if DataFrame is empty, using item_col to generalize.
        return md_string + f"_Ingen {item_col.lower()}er å vise._"
    # Correctly unpack iterrows() while using enumerate for numbering
    for i, (_, row_series) in enumerate(df.iterrows()): # Iterate through aggregated DataFrame rows.
        # Format: "1. ItemName Freq obs | SumInd sum. ind.". Add newline.
        # Use replace(",", " ") for thousand separators in numbers.
        md_string += f"{i + 1}. {row_series[item_col]} {f'{row_series[count_col]:,}'.replace(',', ' ')} obs | {f'{int(row_series[sum_col]):,}'.replace(',', ' ')} sum. ind.\n"
    return md_string # Return the formatted markdown string.

# --- Helper Function: format_top_frequency_md ---
# Formats a value_counts Series into a numbered markdown list.
# Assumes series index is the item (e.g., Art) and values are counts.
def format_top_frequency_md(series, title):
    md_string = f"**{title}**\n" # Start with the title.
    if series.empty:
        return md_string + "_Ingen arter å vise._" # Append message if Series is empty.
    for i, (item, count) in enumerate(series.items()): # Iterate through series items.
        # Format: "1. Count Item". Add newline. Replace comma with space.
        md_string += f"{i + 1}. {f'{count:,}'.replace(',', ' ')} {item}\n"
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
    # Ensure 'Antall Individer' is numeric for calculations
    data['Antall Individer Num'] = pd.to_numeric(data['Antall Individer'], errors='coerce').fillna(0)

    # Top Species by Frequency (Simple Count for col1)
    top_species = data['Art'].value_counts().nlargest(top_n).reset_index()
    top_species.columns = ['Art', 'Antall_Observasjoner'] # Rename for consistency

    # Top Families by Frequency (Simple Count for col4)
    top_families = data['Familie'].value_counts().nlargest(top_n).reset_index()
    top_families.columns = ['Familie', 'Antall_Observasjoner'] # Rename for consistency

    # Top Observers by Frequency (Simple Count)
    top_observers = data["Innsamler/Observatør"].value_counts().nlargest(top_n).reset_index()
    top_observers.columns = ["Innsamler/Observatør", "Antall Observasjoner"] # Re-add column renaming

    # Overall Top 10 Observations by Individual Count (Re-added)
    top_individual_obs = data.nlargest(top_n, 'Antall Individer Num')

    # --- Calculate Category-Specific Top 10 Species (Frequency & Sum Ind.) ---
    # Red List Species Frequencies per Category (with Sum Individuals)
    top_redlist_species_by_cat = {} # Dict to store DataFrames for each category.
    for category in redlist_categories: # Loop through CR, EN, etc.
        category_data = data[data[category_col] == category] # Filter data for this category.
        if not category_data.empty:
            agg_df = category_data.groupby('Art').agg(
                Antall_Observasjoner=('Art', 'size'),
                Sum_Individer=('Antall Individer Num', 'sum')
            ).reset_index()
            top_redlist_species_by_cat[category] = agg_df.nlargest(top_n, 'Antall_Observasjoner') # Calc top 10 and store DF.
        else:
            top_redlist_species_by_cat[category] = pd.DataFrame(columns=['Art', 'Antall_Observasjoner', 'Sum_Individer']) # Store empty DF.

    # Alien Species Frequencies per Category (with Sum Individuals)
    top_alien_species_by_cat = {} # Dict to store DataFrames for each category.
    for category in alien_categories_list: # Loop through SE, HI, etc.
        category_data = data[data[category_col] == category] # Filter data for this risk category.
        if not category_data.empty:
            agg_df = category_data.groupby('Art').agg(
                Antall_Observasjoner=('Art', 'size'),
                Sum_Individer=('Antall Individer Num', 'sum')
            ).reset_index()
            top_alien_species_by_cat[category] = agg_df.nlargest(top_n, 'Antall_Observasjoner') # Calc top 10 and store DF.
        else:
            top_alien_species_by_cat[category] = pd.DataFrame(columns=['Art', 'Antall_Observasjoner', 'Sum_Individer']) # Store empty DF.

    # Special Status Species Frequencies per Column (with Sum Individuals)
    top_special_species_by_col = {} # Dict to store DataFrames for each status.
    special_status_cols = ["Prioriterte Arter", "Andre Spes. Hensyn.", "Ansvarsarter", "Spes. Økol. Former"]
    for status_col in special_status_cols: # Loop through the status column names.
        status_data = data[data[status_col] == 'Yes'] # Filter data where this status is 'Yes'.
        if not status_data.empty:
            agg_df = status_data.groupby('Art').agg(
                Antall_Observasjoner=('Art', 'size'),
                Sum_Individer=('Antall Individer Num', 'sum')
            ).reset_index()
            top_special_species_by_col[status_col] = agg_df.nlargest(top_n, 'Antall_Observasjoner') # Calc top 10 and store DF.
        else:
            top_special_species_by_col[status_col] = pd.DataFrame(columns=['Art', 'Antall_Observasjoner', 'Sum_Individer']) # Store empty DF.

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
        # Conditionally display the Top 10 Species list (Frequency only)
        if st.session_state.show_dashboard_top_lists:
            species_list_md = "**Topp 10 Arter (Hyppighet):**\n" # Title
            if top_species.empty:
                species_list_md += "_Ingen arter å vise._"
            else:
                for index, row in top_species.iterrows():
                    formatted_count = f'{row["Antall_Observasjoner"]:,}'.replace(',', ' ')
                    species_list_md += f"{index + 1}. {formatted_count} {row['Art']}\n"
            st.markdown(species_list_md)
    with col2: # Content for the second column.
        st.metric(label="Totalt Antall Individer", value=f"{total_individuals:,}")  # Display total individuals sum with formatting.
        # RE-ADD: Top 10 Observations by Individual Count display
        if st.session_state.show_dashboard_top_lists:
            st.markdown("**Topp 10 Observasjoner (Individer):**") # Add title
            st.markdown(format_top_observations_md(top_individual_obs)) # Call the formatter
    with col3: # Content for the third column.
        st.metric(label="Unike Arter", value=f"{unique_species:,}")  # Display unique species count.
    with col4: # Content for the fourth column.
        st.metric(label="Unike Familier", value=f"{unique_families:,}")  # Display unique family count.
        # Conditionally display the Top 10 Families list (Frequency only)
        if st.session_state.show_dashboard_top_lists:
            families_list_md = "**Topp 10 Familier (Hyppighet):**\n" # Title
            if top_families.empty:
                families_list_md += "_Ingen familier å vise._"
            else:
                for index, row in top_families.iterrows():
                     formatted_count = f'{row["Antall_Observasjoner"]:,}'.replace(',', ' ')
                     families_list_md += f"{index + 1}. {formatted_count} {row['Familie']}\n"
                st.markdown(families_list_md)
    with col5: # Content for the fifth column.
        st.metric(label="Unike Innsamlere/Observatører", value=f"{unique_observers:,}") # Display unique observer count (which is an int)
        # Conditionally display the Top 10 Observers list (simple format)
        if st.session_state.show_dashboard_top_lists:
            observers_list_md = "**Topp 10 Innsamlere (Hyppighet):**\n" # Start with title.
            if top_observers.empty:
                observers_list_md += "_Ingen innsamlere å vise._"
            else:
                for index, row in top_observers.iterrows():
                    # Format: "1. Count Observer Name". Add newline. Replace comma with space.
                    # Format the count number with spaces as thousand separators first
                    formatted_count = f'{row["Antall Observasjoner"]:,}'.replace(',', ' ')
                    observers_list_md += f"{index + 1}. {formatted_count} {row['Innsamler/Observatør']}\n"
            st.markdown(observers_list_md) # Display the markdown list.


    # --- Individual Red List Category Counts ---
    st.markdown(f"#### Antall Funn per Rødlistekategori (Totalt: {redlisted_total_count:,})")
    rl_cols = st.columns(len(redlist_categories)) # Create columns for each category (Should be 5)
    for i, category in enumerate(redlist_categories): # Iterate through categories and columns
        with rl_cols[i]: # Select the appropriate column
            # Display metric for the specific category count.
            st.metric(label=f"Antall {category}", value=f"{redlist_counts_individual[category]:,}".replace(',', ' '))
            # Conditionally display Top 10 Species for THIS Redlist Category with new format
            if st.session_state.show_dashboard_top_lists:
                top_list_df = top_redlist_species_by_cat.get(category)
                title = f"Topp 10 {category} Arter (Hyppighet | Sum Ind.):"
                st.markdown(format_top_agg_md(top_list_df, title,
                                              item_col='Art',
                                              count_col='Antall_Observasjoner',
                                              sum_col='Sum_Individer'))

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
            st.metric(label=label, value=f"{count:,}".replace(',', ' ')) # Display metric
            # Conditionally display Top 10 Species for THIS Alien Category with new format
            if st.session_state.show_dashboard_top_lists:
                top_list_df = top_alien_species_by_cat.get(category)
                title = f"Topp 10 {category} Arter (Hyppighet | Sum Ind.):"
                st.markdown(format_top_agg_md(top_list_df, title,
                                              item_col='Art',
                                              count_col='Antall_Observasjoner',
                                              sum_col='Sum_Individer'))

    # --- Special Status Counts ---
    st.markdown(f"#### Spesielle Status Markeringer (Totalt Antall 'Yes': {total_special_status_count:,})")
    # Use 5 columns for alignment
    spec_col1, spec_col2, spec_col3, spec_col4, spec_col5 = st.columns(5)
    with spec_col1:
        st.metric(label="Prioriterte Arter", value=f"{prioriterte_count:,}".replace(',', ' '))  # Display count for Prioriterte Arter.
        # Conditionally display Top 10 Species for THIS Special Status Category with new format
        if st.session_state.show_dashboard_top_lists:
            top_list_df = top_special_species_by_col.get("Prioriterte Arter")
            title = "Topp 10 Prioriterte Arter (Hyppighet | Sum Ind.):"
            st.markdown(format_top_agg_md(top_list_df, title,
                                          item_col='Art',
                                          count_col='Antall_Observasjoner',
                                          sum_col='Sum_Individer'))
    with spec_col2:
        st.metric(label="Andre Spes. Hensyn", value=f"{andre_spes_hensyn_count:,}".replace(',', ' '))  # Display count for Andre Spes. Hensyn.
        # Conditionally display Top 10 Species for THIS Special Status Category with new format
        if st.session_state.show_dashboard_top_lists:
            top_list_df = top_special_species_by_col.get("Andre Spes. Hensyn.")
            title = "Topp 10 Andre Spes. Hensyn Arter (Hyppighet | Sum Ind.):"
            st.markdown(format_top_agg_md(top_list_df, title,
                                          item_col='Art',
                                          count_col='Antall_Observasjoner',
                                          sum_col='Sum_Individer'))
    with spec_col3:
        st.metric(label="Ansvarsarter", value=f"{ansvarsarter_count:,}".replace(',', ' '))  # Display count for Ansvarsarter.
        # Conditionally display Top 10 Species for THIS Special Status Category with new format
        if st.session_state.show_dashboard_top_lists:
            top_list_df = top_special_species_by_col.get("Ansvarsarter")
            title = "Topp 10 Ansvarsarter (Hyppighet | Sum Ind.):"
            st.markdown(format_top_agg_md(top_list_df, title,
                                          item_col='Art',
                                          count_col='Antall_Observasjoner',
                                          sum_col='Sum_Individer'))
    with spec_col4:
        st.metric(label="Spes. Økol. Former", value=f"{spes_okol_former_count:,}".replace(',', ' '))  # Display count for Spes. Økol. Former.
        # Conditionally display Top 10 Species for THIS Special Status Category with new format
        if st.session_state.show_dashboard_top_lists:
            top_list_df = top_special_species_by_col.get("Spes. Økol. Former")
            title = "Topp 10 Spes. Økol. Former Arter (Hyppighet | Sum Ind.):"
            st.markdown(format_top_agg_md(top_list_df, title,
                                          item_col='Art',
                                          count_col='Antall_Observasjoner',
                                          sum_col='Sum_Individer'))

    # --- Observation Period ---
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

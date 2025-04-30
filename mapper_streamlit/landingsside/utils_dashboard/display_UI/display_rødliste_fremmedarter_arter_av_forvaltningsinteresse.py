# ##### Imports #####
import streamlit as st # Import Streamlit for UI elements.
import pandas as pd # Import pandas (though mainly used by formatters passed in).

# ##### Display Functions #####

# --- Function: _display_single_status_category ---
# Helper to display metrics and conditional top list for one category/status column.
# Used internally by display_all_status_sections.
def _display_single_status_category(col, label, count, top_list_df, show_top_lists, formatter_agg):
    with col: # Display within the provided Streamlit column object.
        st.metric(label=label, value=f"{count:,}".replace(',', ' ')) # Display the metric count with formatting.
        # Conditionally display Top 10 Species for THIS Category/Status
        if show_top_lists:
            # title = f"Topp 10 {label} (Hyppighet | Sum Ind.):" # Title generated here if needed, but often implied by section.
            # Call the aggregation formatter function.
            st.markdown(formatter_agg(top_list_df, title="", # Pass empty title, handled by section header.
                                      item_col='Art',
                                      count_col='Antall_Observasjoner',
                                      sum_col='Sum_Individer'))

# --- Function: display_all_status_sections ---
# Displays sections for Red List, Alien Species, and Special Status counts and top lists.
# Takes status_counts dict, top_lists dict, show_top_lists bool, and formatters dict.
def display_all_status_sections(status_counts, top_lists, show_top_lists, formatters):
    # Unpack formatters
    format_agg = formatters['format_top_agg_md'] # Get the formatter for aggregated lists.

    # --- Individual Red List Category Counts Section ---
    st.markdown("---") # Add a separator line.
    total_rl = status_counts['redlist_total'] # Get total red list count.
    st.markdown(f"#### Antall Funn per Rødlistekategori (Totalt: {total_rl:,})".replace(',', ' ')) # Section header with total.
    redlist_categories = status_counts['redlist_categories_order'] # Get ordered list of categories.
    rl_cols = st.columns(len(redlist_categories)) # Create columns for each category.

    for i, category in enumerate(redlist_categories): # Iterate through categories and columns.
        count = status_counts['redlist_breakdown'].get(category, 0) # Get count for this category.
        top_list_df = top_lists['top_redlist_species_agg'].get(category) # Get corresponding top list DataFrame.
        label = f"Antall {category}" # Create label for metric.
        _display_single_status_category(rl_cols[i], label, count, top_list_df, show_top_lists, format_agg) # Call helper to display metric and list.

    # --- Individual Alien Species Category Counts Section ---
    st.markdown("---") # Add a separator line.
    total_alien = status_counts['alien_total'] # Get total alien species count.
    st.markdown(f"#### Antall Funn per Fremmedartkategori (Totalt: {total_alien:,})".replace(',', ' ')) # Section header with total.
    alien_categories = status_counts['alien_categories_order'] # Get ordered list of risk categories.
    # Use 5 columns for alignment, categories will fill the first len(alien_categories) columns.
    fa_cols = st.columns(5)

    for i, category in enumerate(alien_categories): # Iterate through the risk categories.
        count = status_counts['alien_breakdown'].get(category, 0) # Get count for this category.
        top_list_df = top_lists['top_alien_species_agg'].get(category) # Get corresponding top list DataFrame.
        label = f"Antall {category}" # Create label for metric.
        _display_single_status_category(fa_cols[i], label, count, top_list_df, show_top_lists, format_agg) # Call helper.

    # --- Special Status Counts Section ---
    st.markdown("---") # Add a separator line.
    total_special = status_counts['special_status_total'] # Get total count for this section.
    st.markdown(f"#### Spesielle Status Markeringer (Totalt Antall 'Yes': {total_special:,})".replace(',', ' ')) # Section header with total.
    special_cols_ordered = status_counts['special_status_cols_order'] # Get ordered list of status columns.
    # Use 5 columns for alignment.
    spec_cols = st.columns(5)

    # Map original column names to shorter labels if desired, or use original names
    special_labels = {
        "Prioriterte Arter": "Prioriterte Arter",
        "Andre Spes. Hensyn.": "Andre Spes. Hensyn",
        "Ansvarsarter": "Ansvarsarter",
        "Spes. Økol. Former": "Spes. Økol. Former"
    }

    # Display each special status category in its own column.
    for i, status_col_name in enumerate(special_cols_ordered): # Iterate through the status columns.
         # Ensure we don't try to access more columns than created (should be 4 statuses, 5 cols).
        if i < len(spec_cols):
            count = status_counts['special_status_breakdown'].get(status_col_name, 0) # Get count.
            top_list_df = top_lists['top_special_species_agg'].get(status_col_name) # Get top list.
            label = special_labels.get(status_col_name, status_col_name) # Get display label.
            _display_single_status_category(spec_cols[i], label, count, top_list_df, show_top_lists, format_agg) # Call helper.

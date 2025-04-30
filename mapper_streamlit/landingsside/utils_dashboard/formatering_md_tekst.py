# ##### Imports #####
import pandas as pd # Import pandas for DataFrame/Series handling.

# ##### Formatting Functions #####

# --- Helper Function: format_top_observations_md ---
# Formats a DataFrame of top observations (by individual count) into a markdown list.
# Assumes df has columns 'Antall Individer Num' (numeric) and 'Art'.
def format_top_observations_md(df):
    md_string = "" # Initialize empty string.
    if df.empty:
        return "_Ingen observasjoner å vise._" # Return message if DataFrame is empty.
    # Ensure 'Antall Individer' is integer for display (using the numeric column)
    df_display = df.copy() # Create a copy to avoid modifying the original DataFrame slice.
    df_display['Antall Individer Display'] = pd.to_numeric(df_display['Antall Individer Num'], errors='coerce').fillna(0).astype(int) # Convert to integer, handling potential errors.
    # Use enumerate to get a counter starting from 0 for correct list numbering (1-based)
    for i, (_, row) in enumerate(df_display.iterrows()): # Use enumerate for 1-based numbering
        # Format: "1. Count Art". Add newline. Use replace for thousands.
        # Pre-format the count number with spaces as thousand separators
        formatted_count = f'{row["Antall Individer Display"]:,}'.replace(',', ' ') # Format number with spaces.
        md_string += f"{i + 1}. {formatted_count} {row['Art']}\n" # Append formatted string.
    return md_string # Return the formatted markdown string.

# --- Helper Function: format_top_agg_md ---
# Formats a DataFrame (result of groupby().agg()) into a numbered markdown list.
# Shows item name, frequency count, and sum of individuals.
# Takes df, title (unused), item_col, count_col, sum_col.
def format_top_agg_md(df, title, item_col, count_col, sum_col):
    # md_string = "**Observasjon | Sum. individ**\n" # REMOVED: Header is now displayed separately.
    md_string = "" # Start with empty string.
    if df.empty:
        # Append message if DataFrame is empty, using item_col to generalize.
        # No header added here anymore.
        return f"_Ingen {item_col.lower()}er å vise._" # Return specific empty message.
    # Correctly unpack iterrows() while using enumerate for numbering
    for i, (_, row_series) in enumerate(df.iterrows()): # Iterate through aggregated DataFrame rows.
        # Format: "1. ItemName Freq | SumInd". Add newline.
        # Use replace(",", " ") for thousand separators in numbers.
        freq_formatted = f'{row_series[count_col]:,}'.replace(',', ' ') # Format frequency count.
        sum_formatted = f'{int(row_series[sum_col]):,}'.replace(',', ' ') # Format sum count (ensure int first).
        md_string += f"{i + 1}. {row_series[item_col]} {freq_formatted} | {sum_formatted}\n" # Append formatted string.
    return md_string # Return the formatted markdown string.

# --- Helper Function: format_top_frequency_md ---
# Formats a value_counts Series or a DataFrame with item/count columns into a numbered markdown list.
# Assumes series index is the item and values are counts, OR df has item_col and count_col.
def format_top_frequency_md(data, title, item_col=None, count_col=None):
    md_string = "" # Start with empty string (title often handled externally).
    if isinstance(data, pd.Series): # Check if input is a Series
        if data.empty:
            return md_string + "_Ingen data å vise._" # Generic empty message for series.
        for i, (item, count) in enumerate(data.items()): # Iterate through series items.
            # Format: "1. Count Item". Add newline. Replace comma with space.
            formatted_count = f'{count:,}'.replace(',', ' ') # Format count.
            md_string += f"{i + 1}. {formatted_count} {item}\n" # Append formatted string.
    elif isinstance(data, pd.DataFrame) and item_col and count_col: # Check if input is DataFrame with specified columns
        if data.empty:
            return md_string + "_Ingen data å vise._" # Generic empty message for DataFrame.
        for i, row in data.iterrows(): # Iterate through DataFrame rows.
            formatted_count = f'{row[count_col]:,}'.replace(',', ' ') # Format count from column.
            md_string += f"{i + 1}. {formatted_count} {row[item_col]}\n" # Append formatted string using specified columns.
    else:
        return md_string + "_Ugyldig input eller manglende kolonner._" # Handle invalid input.

    # Optional: Add title if needed, although usually handled before calling
    # if title:
    #    md_string = f"**{title}**\n" + md_string

    return md_string # Return the formatted markdown string. 
# ##### Imports #####
import plotly.graph_objects as go  # Import Plotly for creating interactive figures.
# import pandas as pd              # Import pandas for type hinting (optional) and data handling. (Unused)
from typing import List            # Import List for type hinting.

# ##### Plotting Function #####


def create_observation_period_figure(yearly_data, traces_to_show: List[str]):
    # --- Function: create_observation_period_figure ---
    # Creates a Plotly figure showing selected yearly observation metrics.
    # Takes a DataFrame and a list of ACTUAL column names (from yearly_data) to display.
    # e.g., traces_to_show might be ['Sum_Observations', 'Sum_Individuals']

    fig = go.Figure()  # Create an empty Plotly figure.

    # --- Define mappings from actual column names to their desired display names for the legend ---
    # These display names should match what the user sees in the multiselect in dashboard.py
    column_to_display_name_map = {
        'Sum_Observations': 'Antall Observasjoner',
        'Sum_Individuals': 'Antall Individer',
        'Avg_Individuals_Per_Observation': 'Gj.snitt Individer/Observasjon'
    }

    # --- Conditionally Add Traces ---
    # Iterate through the actual column names passed in traces_to_show
    for col_name in traces_to_show:
        if col_name == 'Sum_Observations':
            fig.add_trace(go.Scatter(
                x=yearly_data['Year'],
                y=yearly_data['Sum_Observations'],
                mode='lines+markers',
                name=column_to_display_name_map['Sum_Observations'] # Use display name for legend
            ))
        elif col_name == 'Sum_Individuals':
            fig.add_trace(go.Scatter(
                x=yearly_data['Year'],
                y=yearly_data['Sum_Individuals'],
                mode='lines+markers',
                name=column_to_display_name_map['Sum_Individuals'] # Use display name for legend
            ))
        elif col_name == 'Avg_Individuals_Per_Observation':
            fig.add_trace(go.Scatter(
                x=yearly_data['Year'],
                y=yearly_data['Avg_Individuals_Per_Observation'],
                mode='lines+markers',
                name=column_to_display_name_map['Avg_Individuals_Per_Observation'] # Use display name for legend
            ))

    # --- Configure Layout ---
    fig.update_layout(
        title="Observasjoner og Individer per År",
        xaxis_title="År",
        yaxis_title="Verdi", 
        legend_title="Metrikk"
    )

    return fig

# ##### Main Execution Block (Optional) #####
# if __name__ == '__main__':
#     # Example Usage (Requires sample data from calculation)
#     # Import pandas locally if using the example block
#     import pandas as pd
#     sample_yearly_data = pd.DataFrame({
#         'Year': [2020, 2021, 2022],
#         'Sum_Observations': [100, 150, 120],
#         'Sum_Individuals': [500, 700, 600],
#         'Avg_Individuals_Per_Observation': [5.0, 4.67, 5.0]
#     })
#     # Example: Show Sum_Observations and Avg_Individuals_Per_Observation (actual column names)
#     selected_actual_cols = ['Sum_Observations', 'Avg_Individuals_Per_Observation']
#     fig = create_observation_period_figure(sample_yearly_data, traces_to_show=selected_actual_cols)
#     fig.show()  # Display the figure locally.
#     pass        # Keep minimal.

# ##### Imports #####
import plotly.graph_objects as go  # Import Plotly for creating interactive figures.
# import pandas as pd              # Import pandas for type hinting (optional) and data handling. (Unused)
from typing import List            # Import List for type hinting.

# ##### Plotting Function #####


def create_observation_period_figure(yearly_data, traces_to_show: List[str]):
    # --- Function: create_observation_period_figure ---
    # Creates a Plotly figure showing selected yearly observation metrics.
    # Takes a DataFrame and a list of trace names to display.
    # Expected trace names: 'Antall Observasjoner', 'Antall Individer', 'Gj.snitt Individer/Observasjon'

    # --- Initialize Figure ---
    fig = go.Figure()  # Create an empty Plotly figure.

    # --- Define Trace Names ---
    trace_obs = 'Antall Observasjoner'           # Define name for observation count trace.
    trace_ind = 'Antall Individer'             # Define name for individual count trace.
    trace_avg = 'Gj.snitt Individer/Observasjon'  # Define name for average trace.

    # --- Conditionally Add Traces ---
    # Add trace for Sum of Observations if selected
    if trace_obs in traces_to_show:
        fig.add_trace(go.Scatter(
            x=yearly_data['Year'],                  # Set x-axis to Year.
            y=yearly_data['Sum_Observations'],      # Set y-axis to Sum_Observations.
            mode='lines+markers',                 # Use lines and markers for the plot points.
            name=trace_obs                        # Name of the trace for the legend.
        ))

    # Add trace for Sum of Individuals if selected
    if trace_ind in traces_to_show:
        fig.add_trace(go.Scatter(
            x=yearly_data['Year'],                  # Set x-axis to Year.
            y=yearly_data['Sum_Individuals'],       # Set y-axis to Sum_Individuals.
            mode='lines+markers',                 # Use lines and markers.
            name=trace_ind                        # Name of the trace.
        ))

    # Add trace for Average Individuals per Observation if selected
    if trace_avg in traces_to_show:
        fig.add_trace(go.Scatter(
            x=yearly_data['Year'],                            # Set x-axis to Year.
            y=yearly_data['Avg_Individuals_Per_Observation'],  # Set y-axis to the calculated average.
            mode='lines+markers',                           # Use lines and markers.
            name=trace_avg                                  # Name of the trace.
        ))

    # --- Configure Layout ---
    fig.update_layout(
        title="Observasjoner og Individer per År",  # Set the main title of the figure.
        xaxis_title="År",                       # Set the label for the x-axis.
        yaxis_title="Verdi",                      # Use a generic y-axis title as content varies.
        legend_title="Metrikk"                    # Set the title for the legend.
    )

    # --- Return Figure ---
    return fig  # Return the configured Plotly figure object.

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
#     # Example: Show only Observations and Average
#     selected = ['Antall Observasjoner', 'Gj.snitt Individer/Observasjon']
#     fig = create_observation_period_figure(sample_yearly_data, traces_to_show=selected)
#     fig.show()  # Display the figure locally.
#     pass        # Keep minimal.

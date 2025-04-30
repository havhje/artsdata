##### Imports #####
import plotly.graph_objects as go # Import Plotly for creating interactive figures.
import pandas as pd # Import pandas for type hinting (optional) and data handling.

##### Plotting Function #####

# --- Function: create_observation_period_figure ---
# Creates a Plotly figure showing yearly observation metrics.
# Takes a DataFrame with columns: 'Year', 'Sum_Observations', 'Sum_Individuals', 'Avg_Individuals_Per_Observation'.
def create_observation_period_figure(yearly_data):
    # --- Initialize Figure ---
    fig = go.Figure() # Create an empty Plotly figure.

    # --- Add Traces ---
    # Add trace for Sum of Observations
    fig.add_trace(go.Scatter(
        x=yearly_data['Year'], # Set x-axis to Year.
        y=yearly_data['Sum_Observations'], # Set y-axis to Sum_Observations.
        mode='lines+markers', # Use lines and markers for the plot points.
        name='Antall Observasjoner' # Name of the trace for the legend.
    ))

    # Add trace for Sum of Individuals
    fig.add_trace(go.Scatter(
        x=yearly_data['Year'], # Set x-axis to Year.
        y=yearly_data['Sum_Individuals'], # Set y-axis to Sum_Individuals.
        mode='lines+markers', # Use lines and markers.
        name='Antall Individer' # Name of the trace.
    ))

    # Add trace for Average Individuals per Observation
    fig.add_trace(go.Scatter(
        x=yearly_data['Year'], # Set x-axis to Year.
        y=yearly_data['Avg_Individuals_Per_Observation'], # Set y-axis to the calculated average.
        mode='lines+markers', # Use lines and markers.
        name='Gj.snitt Individer/Observasjon' # Name of the trace.
        # yaxis="y2" # Potential secondary axis (commented out for minimal initial implementation).
    ))

    # --- Configure Layout ---
    fig.update_layout(
        title="Observasjoner og Individer per År", # Set the main title of the figure.
        xaxis_title="År", # Set the label for the x-axis.
        yaxis_title="Antall", # Set the label for the primary y-axis.
        # yaxis2=dict( # Configuration for potential secondary y-axis.
        #     title="Gjennomsnitt",
        #     overlaying="y",
        #     side="right"
        # ),
        legend_title="Metrikk" # Set the title for the legend.
    )

    # --- Return Figure ---
    return fig # Return the configured Plotly figure object.

# ##### Main Execution Block (Optional) #####
# if __name__ == '__main__':
#     # Example Usage (Requires sample data from calculation)
#     # sample_yearly_data = pd.DataFrame({
#     #     'Year': [2020, 2021, 2022],
#     #     'Sum_Observations': [100, 150, 120],
#     #     'Sum_Individuals': [500, 700, 600],
#     #     'Avg_Individuals_Per_Observation': [5.0, 4.67, 5.0]
#     # })
#     # fig = create_observation_period_figure(sample_yearly_data)
#     # fig.show() # Display the figure locally.
#     pass # Keep minimal.

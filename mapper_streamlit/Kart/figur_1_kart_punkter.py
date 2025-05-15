import plotly.graph_objects as go
import plotly as plotly


def punktkart(data_fra_kart, color_by):
    # --- Beregner gjennomsnittlig breddegrad og lengdegrad for data ---
    center_lat = data_fra_kart["latitude"].mean()
    center_lon = data_fra_kart["longitude"].mean()

    # --- Beregner farger for hver art i en dictionary ---
    unique_species = data_fra_kart["preferredPopularName"].unique()
    species_color_palette = plotly.colors.qualitative.Dark24
    species_color_map = {species: species_color_palette[i % len(species_color_palette)] for i, species in enumerate(unique_species)}

    # --- Beregner farger for hver familie i en dictionary ---
    unique_families = data_fra_kart["FamilieNavn"].unique()
    family_color_palette = plotly.colors.qualitative.Plotly
    family_color_map = {family: family_color_palette[i % len(family_color_palette)] for i, family in enumerate(unique_families)}

    # --- Fargevalg basert på art eller familie ---
    species_color_list = [species_color_map[species] for species in data_fra_kart["preferredPopularName"]]
    family_color_list = [family_color_map[family] for family in data_fra_kart["FamilieNavn"]]
    color_list = species_color_list if color_by == "Art" else family_color_list

    fig = go.Figure()

    fig.add_trace(
        go.Scattermap(
            lon=data_fra_kart["longitude"],
            lat=data_fra_kart["latitude"],
            mode="markers",  # Type of marker
            marker=dict(size=10, color=color_list, opacity=0.9),
        )
    )

    fig.update_layout(
        showlegend=True,
        height=900,
        width=800,
        map_style="satellite",
        map=dict(
            center=dict(lat=center_lat, lon=center_lon),
            zoom=int(10),
        ),
    )

    return fig

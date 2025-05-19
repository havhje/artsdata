import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer
import streamlit as st

st.set_page_config(page_title="Fuglelydanalyse", layout="wide")
# Import your data
df = pd.read_csv(
    "/Users/havardhjermstad-sollerud/Documents/Kodeprosjekter/python/streamlit/artsdata/databehandling_lyd/data_output_lyd/csvfil/interim/enriched_detections.csv",
    sep=";",
)

pyg_app = StreamlitRenderer(df)

pyg_app.explorer()

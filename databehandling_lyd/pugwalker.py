import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Fuglelydanalyse", layout="wide")

script_dir = Path(__file__).resolve().parent
csv_path = script_dir / "data_output_lyd" / "interim" / "enriched_detections.csv"


df = pd.read_csv(csv_path, sep=";")

pyg_app = StreamlitRenderer(df)

pyg_app.explorer()

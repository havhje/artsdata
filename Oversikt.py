import streamlit as st
import pandas as pd

st.title("Velkommen til artsanalyse")
st.write("Laget av Håvard Hjermstad-Sollerud")
st.subheader("Hva er dette?")
st.write("""
    Dette er en webapplikasjon som gjør at du kan se på data fra Artsdatabanken.
""")

# --- File Upload Section ---
st.subheader("Last opp fil")
artsdata_hovedfil_orginal = st.file_uploader("", type="csv")
artsdata_hovedfil = pd.read_csv(artsdata_hovedfil_orginal, delimiter=';')


# --- Dashboard/KPI ---
st.subheader("Nøkkeltall (KPI)")


# --- table data ---
st.subheader("Hovedoversikt")

st.write(artsdata_hovedfil)

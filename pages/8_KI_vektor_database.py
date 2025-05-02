##### Imports #####
import streamlit as st # Import Streamlit framework
import weaviate # Import weaviate client library
# Removed unused import: import weaviate.classes as wvc
# Removed: from streamlit_weaviate.connection import WeaviateConnection

##### Constants #####
COLLECTION_NAME = "PdfChunks" # Name of the Weaviate collection to query
SEARCH_LIMIT = 5 # Number of search results to retrieve
# Define the properties to retrieve in the search
QUERY_PROPERTIES = ["text_chunk", "source_pdf", "page_number"]

##### Page Configuration #####
st.set_page_config(layout="wide", page_title="PDF Vektor Database Søk") # Set page layout
st.title("Søk i PDF Vektor Database") # Set page title
st.write("Still spørsmål mot innholdet i de indekserte PDF-dokumentene.") # Add introductory text

##### Weaviate Connection & Search Interface #####
conn_error = False # Flag to track connection errors
client = None      # Initialize client to None outside the try block

try:
    print("Attempting Weaviate connection with context manager...") # Log attempt
    # Use context manager to ensure connection is closed automatically
    with weaviate.connect_to_weaviate_cloud(
            cluster_url=st.secrets["WEAVIATE_URL"],
            auth_credentials=weaviate.auth.AuthApiKey(st.secrets["WEAVIATE_API_KEY"]),
            headers={"X-Cohere-Api-Key": st.secrets["COHERE_API_KEY"]}
    ) as client: # Assign to client variable within the context
        print("Weaviate connection successful.") # Log success

        ##### Search Interface (Inside Connection Context) #####
        # Input field for user query
        user_query = st.text_input("Skriv inn ditt søk her:", key="pdf_query_input") # Text input widget

        # Search button
        search_button = st.button("Søk i PDFer", key="pdf_search_button") # Button widget

        # --- Perform Search and Display Results ---
        # Execute search logic only if button is pressed and query exists
        if search_button and user_query:
            st.write("--- Søkeresultater ---") # Separator and header
            # Search errors can still happen, consider a nested try/except here
            # if specific search error handling is needed, otherwise outer handles it.
            pdf_collection = client.collections.get(COLLECTION_NAME)
            response = pdf_collection.query.near_text(
                query=user_query, # The user's search query
                limit=SEARCH_LIMIT, # Limit the number of results
                return_properties=QUERY_PROPERTIES # Specify which properties to return
            )
            if response.objects: # Check if the objects list is not empty
                for i, obj in enumerate(response.objects): # Loop through result objects
                    st.markdown(f"**Resultat {i+1}:**") # Display result number
                    st.markdown(f"> {obj.properties['text_chunk']}") # Display the text chunk (blockquote)
                    st.caption(f"Kilde: {obj.properties['source_pdf']}, Side: {obj.properties['page_number']}") # Display source info
                    st.divider() # Add visual separator
            else:
                st.info("Ingen relevante tekstbiter funnet for ditt søk.") # Message if no results

# --- Exception Handling (after 'with' block) ---
except KeyError as e: # Catch missing secrets specifically during connection attempt
    st.error(f"Feil: Mangler secret '{e}'. Sjekk .streamlit/secrets.toml.") # Show specific error
    conn_error = True # Set error flag
except Exception as e: # Catch other connection or search errors
    st.error(f"Kunne ikke koble til eller søke i Weaviate: {e}") # Show general error
    conn_error = True # Set error flag

# --- Display message if connection failed ---
# This check should happen outside the try/except block
if conn_error:
    st.warning("Weaviate-tilkobling mislyktes. Kan ikke søke.") # Display warning if connection failed 
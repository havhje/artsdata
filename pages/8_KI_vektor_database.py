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

##### Weaviate Connection #####
# Establish connection using secrets from .streamlit/secrets.toml
# Assumes secrets WEAVIATE_URL, WEAVIATE_API_KEY, COHERE_API_KEY are set
conn_error = False # Flag to track connection errors
client: weaviate.WeaviateClient = None # Initialize client variable for later use
try:
    # Removed the attempt to use st.connection as it requires a specific
    # structure in secrets.toml or a missing helper type (streamlit-weaviate).
    # Connecting directly using the weaviate client library.
    print("Attempting manual Weaviate connection...") # Log attempt
    # Use the current recommended connection function
    client = weaviate.connect_to_weaviate_cloud(
            cluster_url=st.secrets["WEAVIATE_URL"],
            auth_credentials=weaviate.auth.AuthApiKey(st.secrets["WEAVIATE_API_KEY"]),
            headers={"X-Cohere-Api-Key": st.secrets["COHERE_API_KEY"]}
    )
    print("Manual Weaviate connection successful.") # Log success

except KeyError as e: # Catch missing secrets
    st.error(f"Feil: Mangler secret '{e}'. Sjekk .streamlit/secrets.toml.") # Show error message
    conn_error = True # Set error flag
except Exception as e: # Catch other connection errors
    st.error(f"Kunne ikke koble til Weaviate: {e}") # Show general connection error
    conn_error = True # Set error flag

##### Search Interface #####
# Only show search interface if connection is successful (client is not None)
if client and not conn_error:
    # Input field for user query
    user_query = st.text_input("Skriv inn ditt søk her:", key="pdf_query_input") # Text input widget

    # Search button
    search_button = st.button("Søk i PDFer", key="pdf_search_button") # Button widget

    # --- Perform Search and Display Results --- 
    # Execute search logic only if button is pressed and query exists
    if search_button and user_query:
        st.write("--- Søkeresultater ---") # Separator and header
        try:
            # Get the collection object from the client
            pdf_collection = client.collections.get(COLLECTION_NAME)

            # Perform the nearText query using the collection object (v4 style)
            response = pdf_collection.query.near_text(
                query=user_query, # The user's search query
                limit=SEARCH_LIMIT, # Limit the number of results
                return_properties=QUERY_PROPERTIES # Specify which properties to return
            )

            # Results are typically in response.objects
            if response.objects: # Check if the objects list is not empty
                # Display each result
                for i, obj in enumerate(response.objects): # Loop through result objects
                    st.markdown(f"**Resultat {i+1}:**") # Display result number
                    # Access properties using obj.properties dictionary
                    st.markdown(f"> {obj.properties['text_chunk']}") # Display the text chunk (blockquote)
                    st.caption(f"Kilde: {obj.properties['source_pdf']}, Side: {obj.properties['page_number']}") # Display source info
                    st.divider() # Add visual separator
            else:
                st.info("Ingen relevante tekstbiter funnet for ditt søk.") # Message if no results

        except Exception as e: # Catch errors during the query execution
            st.error(f"Feil under Weaviate-søk: {e}") # Display error message
            # Optional: Add more specific error handling for Weaviate errors if needed

        # Close the client connection to prevent resource warnings
        client.close() # Ensure the connection is closed after use

else:
    if not conn_error: # Only show this if connection wasn't explicitly flagged as error
        st.warning("Weaviate-klienten ble ikke initialisert.")
    # The error message for conn_error=True is handled within the try/except block 
##### Imports #####
import weaviate # Import the Weaviate client library
import weaviate.classes as wvc # Import Weaviate classes for schema definition etc.
import os # Import os module to access environment variables
import streamlit as st # Import Streamlit (still used for type hints potentially, keep for now)
from pypdf import PdfReader # Import PdfReader from pypdf to read PDF files
from pathlib import Path # Import Path for easier path manipulation
from dotenv import load_dotenv # Import function to load .env file

##### Constants #####
# Define the path to the directory containing PDF files, relative to the project root
PDF_DIRECTORY = Path("mapper_streamlit/KI_vektor/vektor_database")
# Define the name for the Weaviate collection (class)
COLLECTION_NAME = "PdfChunks"
# Define the properties for the objects in the collection
# Using Weaviate Classes config for property definition (Corrected)
PROPERTIES = [
    wvc.config.Property(name="text_chunk", data_type=wvc.config.DataType.TEXT), # The actual text content of the chunk
    wvc.config.Property(name="source_pdf", data_type=wvc.config.DataType.TEXT), # The filename of the PDF the chunk came from
    wvc.config.Property(name="page_number", data_type=wvc.config.DataType.INT) # The page number within the PDF
]
# Define the vectorizer configuration (using Cohere)
# Note: API key is passed via headers during client connection, not directly in schema
VECTORIZER_CONFIG = wvc.config.Configure.Vectorizer.text2vec_cohere()
# Define the generative module configuration (using Cohere)
GENERATIVE_CONFIG = wvc.config.Configure.Generative.cohere()

##### Helper Functions #####

# --- Function: connect_to_weaviate ---
# Connects to the Weaviate instance using credentials from environment variables.
# Returns a Weaviate client object.
def connect_to_weaviate():
    print("Attempting to connect to Weaviate...") # Print status message
    try:
        # Load secrets from environment variables (populated by load_dotenv)
        weaviate_url = os.getenv("WEAVIATE_URL") # Get Weaviate URL from env
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY") # Get Weaviate API key from env
        cohere_api_key = os.getenv("COHERE_API_KEY") # Get Cohere API key from env

        # Check if environment variables were loaded correctly
        if not all([weaviate_url, weaviate_api_key, cohere_api_key]):
            missing = [k for k,v in {"WEAVIATE_URL": weaviate_url, "WEAVIATE_API_KEY": weaviate_api_key, "COHERE_API_KEY": cohere_api_key}.items() if not v]
            print(f"Error: Missing environment variable(s): {', '.join(missing)}. Please check your .env file or environment.")
            raise ValueError("Missing required environment variables for Weaviate connection.")

        # Connect to Weaviate cloud service (Reverted to simpler method)
        client = weaviate.connect_to_wcs(
            cluster_url=weaviate_url, # Pass the cluster URL
            auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key), # Pass the Weaviate API key
            headers={ # Pass additional headers, e.g., for the Cohere API key
                "X-Cohere-Api-Key": cohere_api_key # Header name depends on the vectorizer/generative module used
            }
        )

        print("Successfully connected to Weaviate!") # Print success message
        return client # Return the connected client
    except ValueError as e: # Catch the specific error raised above
        raise
    except Exception as e: # Catch any other connection errors
        print(f"Error connecting to Weaviate: {e}") # Print connection error
        raise # Re-raise the exception

# --- Function: setup_collection ---
# Checks if the collection exists, DELETES it if so, and creates it anew.
# Takes the Weaviate client and collection name.
def setup_collection(client: weaviate.WeaviateClient, collection_name: str):
    print(f"Setting up collection '{collection_name}'...") # Print status message
    # Check if collection already exists
    if client.collections.exists(collection_name): # Use the exists method
        print(f"Collection '{collection_name}' already exists. Deleting for clean import...")
        client.collections.delete(collection_name) # Delete existing collection

    # Proceed to create the collection
    print(f"Creating collection '{collection_name}'...") # Print message if creating
    try:
        # Create the collection with specified properties and vectorizer
        collection = client.collections.create(
            name=collection_name, # Name of the collection
            properties=PROPERTIES, # List of properties defined earlier
            vectorizer_config=VECTORIZER_CONFIG, # Vectorizer configuration
            generative_config=GENERATIVE_CONFIG # Generative module configuration
        )
        print(f"Collection '{collection_name}' created successfully.") # Print success message
        return collection # Return the newly created collection object
    except Exception as e: # Catch errors during collection creation
        print(f"Error creating collection '{collection_name}': {e}") # Print creation error
        raise # Re-raise exception

# --- Function: process_pdf ---
# Reads a PDF, extracts text page by page, splits into paragraphs, and yields data objects.
# Takes the PDF file path. Yields dictionaries for Weaviate import.
def process_pdf(pdf_path: Path):
    print(f"  Processing PDF: {pdf_path.name}") # Print which PDF is being processed
    try:
        reader = PdfReader(pdf_path) # Create a PdfReader object
        # Iterate through each page in the PDF
        for i, page in enumerate(reader.pages): # Loop uses enumerate to get page index (0-based)
            page_number = i + 1 # Get the 1-based page number for user-friendliness
            text = page.extract_text() # Extract text from the current page

            if text: # Proceed only if text was extracted
                # Split text into paragraphs based on double newline characters
                paragraphs = text.split('\n\n') # Split string by double newline
                # Iterate through the extracted paragraphs
                for paragraph in paragraphs: # Loop through the chunks
                    cleaned_paragraph = paragraph.strip() # Remove leading/trailing whitespace
                    # Yield data only if the paragraph is not empty after stripping
                    if cleaned_paragraph: # Check if the cleaned chunk is non-empty
                        # Yield a dictionary representing the object to be imported
                        yield {
                            "text_chunk": cleaned_paragraph, # The text content
                            "source_pdf": pdf_path.name, # The source PDF filename
                            "page_number": page_number # The page number
                        }
    except Exception as e: # Catch errors during PDF reading/processing
        print(f"  Error processing {pdf_path.name}: {e}") # Print processing error for the specific PDF

##### Main Ingestion Logic #####

# --- Function: main ---
# Orchestrates the PDF ingestion process.
def main():
    # Load environment variables from .env file at the start of main execution
    load_dotenv() 
    print("Starting PDF ingestion script...") # Script start message
    client = connect_to_weaviate() # Establish connection to Weaviate
    collection = setup_collection(client, COLLECTION_NAME) # Ensure the collection exists (creates anew)

    pdf_files = list(PDF_DIRECTORY.glob("*.pdf")) # Find all PDF files in the specified directory
    print(f"Found {len(pdf_files)} PDF files in '{PDF_DIRECTORY}'.") # Print number of PDFs found

    # Reverted to using dynamic batching associated with the collection
    # Removed explicit batch size configuration

    with collection.batch.dynamic() as batch: # Use collection's dynamic batching
        print("Starting dynamic batch import...")
        processed_files = 0 # Counter for processed files
        total_chunks = 0 # Counter for total chunks added
        # Iterate through each found PDF file
        for pdf_path in pdf_files: # Loop through PDF file paths
            chunk_count_for_file = 0 # Counter for chunks from the current file
            # Process each PDF and get data objects (paragraphs)
            for data_object in process_pdf(pdf_path): # Loop through yielded data objects
                # Add object directly using collection's batch manager
                batch.add_object(
                    properties=data_object # Pass the dictionary as properties
                )
                chunk_count_for_file += 1 # Increment chunk counter for the file
                total_chunks += 1 # Increment total chunk counter
            # Print progress after processing each file
            if chunk_count_for_file > 0: # Only print if chunks were found
                 print(f"    Added {chunk_count_for_file} chunks from {pdf_path.name}.")
            processed_files += 1 # Increment processed file counter

    print("Batch import completed.") # Batch end message
    print(f"Processed {processed_files} PDF files.") # Summary: files processed
    print(f"Added a total of {total_chunks} text chunks to the '{COLLECTION_NAME}' collection.") # Summary: chunks added

    client.close() # Close the Weaviate client connection
    print("Weaviate connection closed.") # Confirmation message
    print("Ingestion script finished.") # Script end message

# --- Script Execution ---
# Standard Python entry point check
if __name__ == "__main__":
    # Removed the st.secrets check as we now use dotenv
    main() # Call the main function to start the process 
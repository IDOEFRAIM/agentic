# Importing the necessary modules from the chromadb package:
# chromadb is used to interact with the Chroma DB database,
# embedding_functions is used to define the embedding model
import chromadb
from chromadb.utils import embedding_functions

#We re defining the embedding function using SentenceTransformers
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# We re creating a new instance of ChromaClient to interact with the Chroma DB
client = chromadb.Client()

#It defines the name for the collection to be created or retrieved
collection_name = "my_grocery_collection"

# Define the main function to interact with the Chroma DB
def main():
    try:

# distance metric, and embedding function. In this case, we are using 
# cosine distance
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "A collection for storing grocery data"},
            configuration={
                "hnsw": {"space": "cosine"},
                "embedding_function": ef
            }
        )
        print(f"Collection created: {collection.name}")
        pass
    except Exception as error:  # Catch any errors and log them to the console
        print(f"Error: {error}")



# Array of grocery-related text items
texts = [
    'fresh red apples',
    'organic bananas',
    'ripe mangoes',
    'whole wheat bread',
    'farm-fresh eggs',
    'natural yogurt',
    'frozen vegetables',
    'grass-fed beef',
    'free-range chicken',
    'fresh salmon fillet',
    'aromatic coffee beans',
    'pure honey',
    'golden apple',
    'red fruit'
]

# Create a list of unique IDs for each text item in the 'texts' array
 # Each ID follows the format 'food_<index>', where <index> starts from 1
ids = [f"food_{index + 1}" for index, _ in enumerate(texts)]

# Add documents and their corresponding IDs to the collection
# The `add` method inserts the data into the collection
# The documents are the actual text items, and the IDs are unique identifiers
# ChromaDB will automatically generate embeddings using the configured embedding function
collection.add(
    documents=texts,
    metadatas=[{"source": "grocery_store", "category": "food"} for _ in texts],
    ids=ids
)

# Retrieve all the items (documents) stored in the collection
# The `get` method fetches all data from the collection
all_items = collection.get()
# Log the retrieved items to the console for inspection
# This will print out all the documents, IDs, and metadata stored in the collection
print("Collection contents:")
print(f"Number of documents: {len(all_items['documents'])}")


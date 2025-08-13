from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import SimpleDirectoryReader
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from google.genai.types import EmbedContentConfig
from llama_index.llms.google_genai import GoogleGenAI
import os

from openai import vector_stores

GOOGLE_API_KEY ="AIzaSyBgryLDVFMEG0OqBkCS1LVCnfO9c6rmTJ0"
print("API_KEY",GOOGLE_API_KEY)
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

Settings.llm = GoogleGenAI()
Settings.embed_model = GoogleGenAIEmbedding(
    model_name="text-embedding-004",
    embed_batch_size=100,
    # can pass in the api key directly
    # api_key="...",
    # or pass in a vertexai_config
    # vertexai_config={
    #     "project": "...",
    #     "location": "...",
    # }
    # can also pass in an embedding_config
    # embedding_config=EmbedContentConfig(...)
)

filename_fn = lambda filename: {"file_name": filename}

# automatically sets the metadata of each document according to filename_fn
documents = SimpleDirectoryReader(
    "../documents", file_metadata=filename_fn
).load_data()

vector_store=SimpleVectorStore()

# create the pipeline with transformations
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=25, chunk_overlap=0),
        TitleExtractor()
    ],
    vector_store=vector_store
)

node=pipeline.run(documents=documents)

index = VectorStoreIndex(node,storage_context=StorageContext.from_defaults(vector_store=vector_store))

query_engine = index.as_query_engine()
response=query_engine.query("Who is Kalyan?")
print(response)
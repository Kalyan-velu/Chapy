from storage.paths import source_pdf_path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext
from llama_index.core.extractors import TitleExtractor, QuestionsAnsweredExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter, TokenTextSplitter
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.readers.file import PDFReader
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
)

document_indexes={}

def remove_index(document_id: str):
    document_indexes.pop(document_id, None)

def get_query_engine(document_id: str):
    index = document_indexes.get(document_id)
    if index is None:
        index = get_index(document_id)
    return index.as_query_engine()


def get_index(document_id: str ):
    # automatically sets the metadata of each document according to filename_fn
    documents = PDFReader().load_data(
        file=source_pdf_path(document_id=document_id),
    )

    vector_store = SimpleVectorStore()

    text_splitter = TokenTextSplitter(
        separator=" ", chunk_size=512, chunk_overlap=128
    )
    title_extractor = TitleExtractor(nodes=5)
    qa_extractor = QuestionsAnsweredExtractor(questions=3)
    token_text_splitter = TokenTextSplitter(
        separator=" ", chunk_size=512, chunk_overlap=128
    )
    # create the pipeline with transformations
    pipeline = IngestionPipeline(
        transformations=[
            text_splitter, qa_extractor,title_extractor, token_text_splitter
        ],
        vector_store=vector_store

    )

    node = pipeline.run(documents=documents, in_place=True,
                        show_progress=True, )

    index = VectorStoreIndex(node, storage_context=StorageContext.from_defaults(vector_store=vector_store))
    document_indexes[document_id]=index
    return index


from llm.rag import get_index


def create_chat(doc_id:str):
    index = get_index(doc_id)
    query_engine = index.as_query_engine()

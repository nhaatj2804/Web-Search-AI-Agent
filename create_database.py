from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.vectorstores import Chroma
import os
import shutil
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from pathlib import Path


import uuid

CHROMA_BASE_PATH = "chroma"
DATA_PATH = "data"
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="intfloat/e5-small-v2")

def get_collection_path(collection_id: str) -> str:
    """Get the path for a specific collection"""
    return os.path.join(CHROMA_BASE_PATH, collection_id)

def get_chroma_session(collection_id: str = None):
    """Get a ChromaDB session for a specific collection"""
    if collection_id is None:
        collection_id = str(uuid.uuid4())
    
    collection_path = get_collection_path(collection_id)
    if not os.path.exists(collection_path):
        os.makedirs(collection_path, exist_ok=True)
    
    return Chroma(
        persist_directory=collection_path,
        embedding_function=EMBEDDING_MODEL
    ), collection_id

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
        is_separator_regex=False,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_documents(documents)

def save_to_chroma(chunks: list[Document], collection_id: str = None):
    """Add documents to a new ChromaDB collection"""
    # Create a new collection for this set of documents
    db, collection_id = get_chroma_session(collection_id)
    
    # Add documents to the new collection
    db.add_documents(documents=chunks)
    db.persist()
    print(f"Added {len(chunks)} chunks to collection {collection_id}")
    
    return collection_id

def load_documents(collection_id: str = None):
    documents = []
    search_path = Path(DATA_PATH)
    if collection_id:
        search_path = search_path / collection_id
    for path in search_path.glob("*.md"):
        loader = TextLoader(path.as_posix())
        documents.extend(loader.load())
    return documents
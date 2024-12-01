from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from langchain.docstore.document import Document
from typing import List


def split_code2docs(text: str) -> List[Document]:
    #TODO use lang guesses
    #TODO use better chunking
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=4096, chunk_overlap=100)
    
    docs = splitter.create_documents([text])
    return docs


def split_docs(text: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN ,chunk_size=128, chunk_overlap=32)
    
    docs = splitter.create_documents([text])
    return [d.page_content for d in docs]
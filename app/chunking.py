from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from langchain.docstore.document import Document
from typing import List
from __future__ import annotations
from tree_sitter_languages import get_language, get_parser
from dataclasses import dataclass
from tree_sitter import Node, Tree
import re

 
@dataclass
class Span:
    start: int
    end: int
 
    def extract(self, s: str) -> str:
        return s[self.start: self.end]
 
    def extract_lines(self, s: str) -> str:
        return "\n".join(s.splitlines()[self.start:self.end])
 
    def __add__(self, other: Span | int) -> Span:
        if isinstance(other, int):
            return Span(self.start + other, self.end + other)
        elif isinstance(other, Span):
            return Span(self.start, other.end)
        else:
            raise NotImplementedError()
 
    def __len__(self) -> int:
        return self.end - self.start
 
def non_whitespace_len(s: str) -> int: # new len function
    return len(re.sub("\s", "", s))

def get_line_number(index: int, source_code: str) -> int:
    total_chars = 0
    for line_number, line in enumerate(source_code.splitlines(keepends=True), start=1):
        total_chars += len(line)
        if total_chars > index:
            return line_number - 1
    return line_number


def chunker(
	tree: Tree,
	source_code: bytes,
	MAX_CHARS=512 * 3,
	coalesce=50 # Any chunk less than 50 characters long gets coalesced with the next chunk
) -> list[Span]:
 
    # 1. Recursively form chunks 
    def chunk_node(node: Node) -> list[Span]:
        chunks: list[Span] = []
        current_chunk: Span = Span(node.start_byte, node.start_byte)
        node_children = node.children
        for child in node_children:
            if child.end_byte - child.start_byte > MAX_CHARS:
                chunks.append(current_chunk)
                current_chunk = Span(child.end_byte, child.end_byte)
                chunks.extend(chunk_node(child))
            elif child.end_byte - child.start_byte + len(current_chunk) > MAX_CHARS:
                chunks.append(current_chunk)
                current_chunk = Span(child.start_byte, child.end_byte)
            else:
                current_chunk += Span(child.start_byte, child.end_byte)
        chunks.append(current_chunk)
        return chunks
    chunks = chunk_node(tree.root_node)
 
    # 2. Filling in the gaps
    for prev, curr in zip(chunks[:-1], chunks[1:]):
        prev.end = curr.start
    curr.start = tree.root_node.end_byte
 
    # 3. Combining small chunks with bigger ones
    new_chunks = []
    current_chunk = Span(0, 0)
    for chunk in chunks:
        current_chunk += chunk
        if non_whitespace_len(current_chunk.extract(source_code)) > coalesce \
            and "\n" in current_chunk.extract(source_code):
            new_chunks.append(current_chunk)
            current_chunk = Span(chunk.end, chunk.end)
    if len(current_chunk) > 0:
        new_chunks.append(current_chunk)
 
    # 4. Changing line numbers
    line_chunks = [Span(get_line_number(chunk.start, source_code),
                    get_line_number(chunk.end, source_code)) for chunk in new_chunks]
 
    # 5. Eliminating empty chunks
    line_chunks = [chunk for chunk in line_chunks if len(chunk) > 0]
 
    return line_chunks



def split_code2docs(text: str) -> List[str]:
    #TODO use lang guesses

    language = get_language("python")
    parser = get_parser("python")
    
    tree = parser.parse(text.encode("utf-8"))
    res = []
    for chunk in chunker(tree, text):
        res.append(chunk.extract_lines(text))
    return res



def split_docs(text: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN ,chunk_size=128, chunk_overlap=32)
    
    docs = splitter.create_documents([text])
    return [d.page_content for d in docs]

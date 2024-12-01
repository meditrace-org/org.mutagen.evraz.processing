from app.chunking import split_docs
from settings import settings
import bm25s
import Stemmer


class StorageBM:
    def __init__(self):
        self.retriever = bm25s.BM25()
        self.stemmer = Stemmer.Stemmer("russian")


    def add(self, doc):
        self.docs = split_docs(doc)
        corpus_tokens = bm25s.tokenize(self.docs, stopwords="ru", stemmer=self.stemmer)
        self.retriever.index(corpus_tokens)


    def get(self, query):
        res = []
        results, scores =  self.retriever.retrieve(bm25s.tokenize(query, stemmer=self.stemmer), k=settings.top_k_docstore)
        for i in range(results.shape[1]):
            doc, score = results[0, i], scores[0, i]
            res.append(self.docs[doc])
        return res


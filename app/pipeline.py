from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.docstore.document import Document
from model import APIModel
from settings import prompts, settings
from typing import List, Optional
from pydantic import BaseModel, Field
from vectorstore import store



# Pydantic
class CodeReview(BaseModel):
    """Review for the code chunk"""

    remark: str = Field(description="Type of issue of the code, two words only. For example architecture issue or inconsistency issue")
    feedback: str = Field(description="Brief feedback on the code chunk.")
    rating: int = Field(
        default=5, description="Rating of the code chunk, from 1 to 10"
    )


class Pipeline:

    def __init__(self):

        parser = PydanticOutputParser(pydantic_object=CodeReview)
        prompt = ChatPromptTemplate.from_messages([
        ("system", "Wrap the output in `json` format following the schema below\n{format_instructions}"),
        ( "human", "Please, review this code:{query} "), ]).partial(format_instructions=parser.get_format_instructions())


        self.docs_helper = APIModel(endpoint=settings.api, 
                                    model=settings.model, 
                                    key=settings.key, 
                                    max_tokens=settings.max_tokens, 
                                    temperature=settings.temperature, 
                   system_prompt=prompts.docs_seeker)
        
        code_reviewer = APIModel(endpoint=settings.api, 
                                    model=settings.model, 
                                    key=settings.key, 
                                    max_tokens=settings.max_tokens, 
                                    temperature=settings.temperature,  
                   system_prompt=prompts.code_reviewer)

        self.summary = APIModel(endpoint=settings.api, 
                                    model=settings.model, 
                                    key=settings.key, 
                                    max_tokens=settings.max_tokens, 
                                    temperature=settings.temperature,  
                   system_prompt=prompts.summarier)
 
        self.chain = prompt | code_reviewer | parser

    def execute(self, chunk: str):
        query = self.docs_helper(chunk)
        print(query)
        docs = store.get(query) 
        chunk = chunk + "\n" + f"Do the review in strict accordance with the following rules: {', '.join(docs)}"
        return self.chain.invoke(chunk)
    

    def __call__(self, chunks: List[str], store):

        self.history = []
        rating = 0
        for chunk in chunks:
            try:
                output = self.execute(chunk)
                self.history.append(
                {
                "chunk": chunk,
                "review": output
                })

                rating += output.rating
            except Exception as e:
                print(e)

        print(f"TOTAL rating: {rating / len(chunks)}")
        return self.report()
    
    def report(self):
        total = ""

        for h in self.history:
            total += f'### {h["review"].remark}:\n {h["review"].feedback}'

        self.history = []
        review = self.summary(total)
        
        return review + '\n' + total

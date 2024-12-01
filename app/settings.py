from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api: str
    key: str

    model: str = "mistral-nemo-instruct-2407"
    max_tokens: int = 1024
    temperature: float = 0.3
    top_k_docstore: int = 4

    ampq_user: str
    ampq_password: str
    ampq_host: str
    ampq_port: int
    ampq_vir_host: str

    queue_in: str = "uploaded_to_review"
    queue_back: str = "ampq_password"
    prefetch_count: int = 1


class Prompts(BaseSettings):

    docs_seeker: str = """
    Напиши запрос в векторную базу с документами и правилами компании о разработке, который самым наилучшим образовом получит необходимые правила для следующего кода. Никогда не забывай про самые важные правила, которые подходят для любого кода.  
    """.strip()

    code_reviewer: str = """
    Instruction: You are an advanced AI model trained to perform detailed code reviews.Your task is to analyze code snippets provided to you, assess their quality, adherence to best practices, and logical soundness, and provide actionable feedback.Follow the rules and guidelines below rigorously when conducting the review.
    Always check the code for compliance with the rules and standards described below, even if it may not be completely correct. The correctness of the code and the entire infrastructure of the company depend on this, otherwise millions of users will not be able to use the services that are being reviewed.
    documents.
    """.strip()

    summarier: str = """
    Instruction: Write brief summary of code review using these remarks. If code is good or has errors always say about it.
    """.strip()


settings = Settings()
prompts = Prompts()

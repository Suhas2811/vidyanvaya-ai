import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL_NAME = "gpt-5.6-luna"


def generate_openai_answer(question, context):
    """
    Generate an academic answer using OpenAI.

    The API key is checked when this provider is called,
    so a missing key can cleanly fall through to the
    next provider in the fallback chain.
    """

    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not set in the .env file."
        )

    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        temperature=0.0,
        max_retries=0,
        timeout=45,
    )

    prompt = f"""
You are VidyānVaya AI, an academic learning assistant.

Answer the student's question using the supplied academic
context as the primary source.

Rules:
1. Stay grounded in the academic context.
2. Use definitions, concepts, formulas, methods, and examples
   supported by the context.
3. You may perform calculations and logical reasoning using
   concepts or formulas present in the context.
4. Do not introduce unrelated external facts.
5. If the context is insufficient to answer reliably, clearly
   state that the uploaded materials do not contain enough
   information.
6. Give a clear, accurate, student-friendly answer.

Academic Context:
-----------------
{context}
-----------------

Student Question:
{question}

Now answer the student's question.
"""

    response = llm.invoke(prompt)

    return response.content
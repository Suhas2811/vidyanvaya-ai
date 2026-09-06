import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def generate_openai_answer(question, context):
    """
    Generate a grounded academic answer using OpenAI.
    """

    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not set in the .env file."
        )

    llm = ChatOpenAI(
        model="gpt-5.6-luna",
        api_key=OPENAI_API_KEY,
        max_retries=2,
    )

    prompt = f"""
You are VidyānVaya AI, an academic learning assistant.

Answer the student's question using the provided
academic context as the primary source.

Rules:

1. Use the academic context for facts, definitions,
   concepts, formulas, methods, and examples.

2. You may solve numerical questions using formulas
   and methods supported by the context.

3. Do not introduce unrelated external information.

4. Show calculation steps when required.

5. If the context does not contain enough information
   to answer reliably, say:

"I could not find enough information in the uploaded
materials to answer this question."

6. Give a clear and student-friendly answer.

Academic Context:
-----------------
{context}
-----------------

Student Question:
{question}

Now answer the student's question.
"""

    response = llm.invoke(prompt)

    return response.text
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL_NAME = "gemini-3.6-flash"


def generate_answer(question, context):
    """
    Generate a grounded academic answer using
    the retrieved document context.
    """

    prompt = f"""
You are VidyānVaya AI, an academic learning assistant.

Your task is to answer the student's question using the
provided academic context as the primary source.

IMPORTANT RULES:

1. Use the academic context for facts, definitions,
   concepts, formulas, methods, and examples.

2. If the exact question or exact numerical values are
   not present in the context, you may still solve the
   question using formulas, concepts, and methods that
   ARE present in the context.

3. You may perform mathematical calculations and logical
   reasoning based on the information provided in the
   academic context.

4. Do NOT introduce unrelated external facts or information
   that are not supported by the academic context.

5. If the context contains a relevant formula or method,
   explain how it is applied to the student's question.

6. Show the calculation steps clearly when the question
   requires a numerical solution.

7. If the academic context does not contain enough
   information, formula, concept, or method to answer the
   question reliably, say:
   "I could not find enough information in the uploaded
   materials to answer this question."

8. Do not simply say that the exact answer is missing.
   First check whether the answer can be derived from the
   concepts or formulas in the context.

9. Give a clear, accurate, student-friendly answer.

Academic Context:
-----------------
{context}
-----------------

Student Question:
{question}

Now answer the student's question.
"""

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt
    )

    return interaction.output_text
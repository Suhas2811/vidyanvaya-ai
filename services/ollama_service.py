from langchain_ollama import ChatOllama


MODEL_NAME = "qwen3:4b"


llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0,
)


def generate_ollama_answer(question, context):
    """
    Generate a grounded academic answer using
    the local Ollama model.
    """

    prompt = f"""
You are VidyānVaya AI, an academic learning assistant.

Answer the student's question using the provided
academic context as the primary source.

IMPORTANT RULES:

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

7. Do not reveal your internal reasoning or thinking process.

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
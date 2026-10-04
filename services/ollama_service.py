from langchain_ollama import ChatOllama


MODEL_NAME = "qwen3:4b"


def generate_ollama_answer(question, context):
    """
    Generate an academic answer using the local Ollama model.

    Ollama is the final fallback provider, so it has a bounded
    timeout to prevent the application from hanging indefinitely.
    """

    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=0.0,
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
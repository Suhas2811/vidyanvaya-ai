from services.llm_service import generate_answer
from services.openai_service import generate_openai_answer
from services.ollama_service import generate_ollama_answer


PROVIDER_ORDER = ["gemini", "openai", "ollama"]


def generate_with_provider(provider, question, context):
    """
    Generate an answer using one explicitly selected provider.
    """

    if provider == "gemini":
        return generate_answer(question, context)

    if provider == "openai":
        return generate_openai_answer(question, context)

    if provider == "ollama":
        return generate_ollama_answer(question, context)

    raise ValueError(f"Unsupported AI provider: {provider}")


def generate_with_fallback(question, context):
    """
    Try providers in order and immediately fall back when one
    provider fails or times out.

    Provider order:
        1. Gemini
        2. OpenAI
        3. Ollama
    """

    errors = []

    for provider in PROVIDER_ORDER:
        try:
            answer = generate_with_provider(
                provider,
                question,
                context,
            )

            if answer is None or not str(answer).strip():
                raise ValueError("Provider returned an empty response.")

            return str(answer), provider

        except Exception as error:
            error_message = str(error).strip()

            if not error_message:
                error_message = error.__class__.__name__

            errors.append(
                f"{provider.upper()}: {error_message}"
            )

    raise RuntimeError(
        "All AI providers failed.\n\n"
        + "\n".join(errors)
    )
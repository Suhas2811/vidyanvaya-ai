from services.llm_service import generate_answer
from services.openai_service import generate_openai_answer
from services.ollama_service import generate_ollama_answer


def generate_with_provider(provider, question, context):

    if provider == "gemini":
        return generate_answer(question, context)

    if provider == "openai":
        return generate_openai_answer(question, context)

    if provider == "ollama":
        return generate_ollama_answer(question, context)

    raise ValueError(f"Unsupported AI provider: {provider}")


def generate_with_fallback(question, context):

    providers = [
        "gemini",
        "openai",
        "ollama",
    ]

    errors = []

    for provider in providers:

        try:
            answer = generate_with_provider(
                provider,
                question,
                context
            )

            return answer, provider

        except Exception as error:

            error_message = str(error)

            errors.append(
                f"{provider.upper()}: {error_message}"
            )

            continue

    raise RuntimeError(
        "All AI providers failed.\n\n"
        + "\n".join(errors)
    )
from services.llm_service import generate_answer
from services.openai_service import generate_openai_answer
from services.ollama_service import generate_ollama_answer


def generate_with_provider(
    provider,
    question,
    context
):
    """
    Generate an answer using the selected AI provider.
    """

    if provider == "gemini":
        return generate_answer(
            question,
            context
        )

    if provider == "openai":
        return generate_openai_answer(
            question,
            context
        )

    if provider == "ollama":
        return generate_ollama_answer(
            question,
            context
        )

    raise ValueError(
        f"Unsupported AI provider: {provider}"
    )


def is_provider_failure(error):
    """
    Determine whether an error is likely caused by
    an unavailable AI provider.

    Fallback should happen for provider availability
    problems, not for normal programming or prompt errors.
    """

    error_text = str(error).lower()
    error_type = type(error).__name__.lower()

    failure_keywords = [
        "rate limit",
        "ratelimit",
        "quota",
        "too many requests",
        "timeout",
        "timed out",
        "connection",
        "connecterror",
        "connectionerror",
        "service unavailable",
        "temporarily unavailable",
        "internal server error",
        "bad gateway",
        "gateway timeout",
        "503",
        "502",
        "500",
        "401",
        "403",
        "api key",
        "authentication",
        "unauthorized",
    ]

    return (
        any(
            keyword in error_text
            for keyword in failure_keywords
        )
        or "timeout" in error_type
        or "connection" in error_type
    )


def generate_with_fallback(
    question,
    context
):
    """
    Try multiple AI providers in sequence.

    Provider order:
    1. Gemini
    2. OpenAI
    3. Ollama

    Returns:
        tuple:
            (answer, provider_used)
    """

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

            if not is_provider_failure(error):
                raise

            errors.append(
                f"{provider}: {error}"
            )

            continue

    raise RuntimeError(
        "All AI providers failed.\n\n"
        + "\n".join(errors)
    )
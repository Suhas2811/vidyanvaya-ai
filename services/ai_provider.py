import time

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

    Diagnostic timing is printed to the terminal so provider
    performance can be identified without changing the
    application's behavior.
    """

    errors = []

    print("\n" + "=" * 60)
    print("[AI] Starting provider fallback chain")
    print(f"[AI] Provider order: {PROVIDER_ORDER}")
    print("=" * 60)

    for provider in PROVIDER_ORDER:

        print(f"\n[AI] Trying provider: {provider.upper()}")

        start_time = time.perf_counter()

        try:
            answer = generate_with_provider(
                provider,
                question,
                context,
            )

            elapsed_time = time.perf_counter() - start_time

            if answer is None or not str(answer).strip():
                raise ValueError("Provider returned an empty response.")

            print(
                f"[AI] {provider.upper()} succeeded "
                f"in {elapsed_time:.2f} seconds."
            )

            print("=" * 60)
            print(
                f"[AI] Selected provider: {provider.upper()} "
                f"({elapsed_time:.2f}s)"
            )
            print("=" * 60)

            return str(answer), provider

        except Exception as error:

            elapsed_time = time.perf_counter() - start_time

            error_message = str(error).strip()

            if not error_message:
                error_message = error.__class__.__name__

            print(
                f"[AI] {provider.upper()} failed "
                f"after {elapsed_time:.2f} seconds."
            )

            print(f"[AI] Error: {error_message}")

            errors.append(
                f"{provider.upper()}: {error_message}"
            )

    print("\n" + "=" * 60)
    print("[AI] ALL PROVIDERS FAILED")
    print("=" * 60)

    raise RuntimeError(
        "All AI providers failed.\n\n"
        + "\n".join(errors)
    )
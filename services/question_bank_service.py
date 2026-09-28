import json
import re

from services.ai_provider import generate_with_fallback


# ==================================================
# JSON CLEANING
# ==================================================

def _clean_json_response(response_text):
    text = str(response_text).strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE
        )
        text = re.sub(
            r"\s*```$",
            "",
            text
        )

    return text.strip()


def _extract_json_array(response_text):
    cleaned = _clean_json_response(response_text)

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "AI response did not contain a valid JSON array."
        )

    return json.loads(
        cleaned[start:end + 1]
    )


# ==================================================
# QUESTION VALIDATION
# ==================================================

def _normalise_questions(questions):
    if not isinstance(questions, list):
        raise ValueError(
            "AI returned an invalid question list."
        )

    normalised = []

    for index, item in enumerate(
        questions,
        start=1
    ):

        if not isinstance(item, dict):
            continue

        question_text = str(
            item.get(
                "question_text",
                item.get("question", "")
            )
        ).strip()

        if not question_text:
            continue

        question_number = str(
            item.get(
                "question_number",
                index
            )
        ).strip()

        normalised.append(
            {
                "question_number": question_number,
                "question_text": question_text,
            }
        )

    if not normalised:
        raise ValueError(
            "No usable questions were returned by the AI."
        )

    return normalised


# ==================================================
# QUESTION EXTRACTION
# ==================================================

def extract_questions(question_paper_text):
    """
    Extract individual questions from a question paper.

    The prompt is intentionally compact because question papers can
    contain OCR noise and formatting that should not be repeated in
    the instructions. Provider fallback is handled by ai_provider.py.
    """

    text = str(
        question_paper_text or ""
    ).strip()

    if not text:
        raise ValueError(
            "Question paper text is empty."
        )

    # Keep the input bounded. For normal question papers this preserves
    # the complete text. Very large papers are already chunked by main.py.
    max_input_chars = 18000
    if len(text) > max_input_chars:
        text = text[:max_input_chars]

    prompt = f"""
Extract every individual examination question from the question paper below.

Return ONLY a JSON array.
Each item must contain exactly:
- "question_number"
- "question_text"

Preserve the original wording as closely as possible.
Keep sub-parts such as (a), (b), and (c) together with their parent question.
Do not create explanations, answers, summaries, or duplicate questions.
Do not invent missing text.

QUESTION PAPER:
{text}
"""

    response_text, provider_used = generate_with_fallback(
        prompt,
        ""
    )

    questions = _extract_json_array(
        response_text
    )

    questions = _normalise_questions(
        questions
    )

    # Give stable numbering if the model returned inconsistent numbering.
    for index, question in enumerate(
        questions,
        start=1
    ):
        question["question_number"] = str(index)

    return questions, provider_used

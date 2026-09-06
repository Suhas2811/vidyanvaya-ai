import json
import re

from services.ai_provider import generate_with_fallback


def clean_json_response(response):
    """
    Remove common Markdown code fences from an LLM response.
    """

    response = response.strip()

    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"\s*```$",
        "",
        response
    )

    return response.strip()


def extract_questions(text):
    """
    Extract individual questions from an academic
    question paper.

    Returns:
        questions, provider_used
    """

    prompt = """
You are VidyānVaya AI, an academic question-paper
processing assistant.

Your task is to extract individual questions from the
provided question paper text.

IMPORTANT RULES:

1. Extract only actual questions from the text.

2. Preserve the original wording of each question as
   closely as possible.

3. Do not answer or solve the questions.

4. Do not invent questions.

5. Do not combine separate questions into one question.

6. Ignore page numbers, headers, footers, college names,
   instructions, marks information, and other non-question
   content unless they are part of the question itself.

7. Preserve the question numbering when it is available.

8. If a question has sub-parts such as (a), (b), (c),
   keep the complete question together.

9. Return ONLY valid JSON.

10. Use exactly this JSON structure:

[
    {
        "question_number": "1",
        "question_text": "Complete question text"
    }
]

11. If no questions can be identified, return:

[]

Question Paper Text:
--------------------
""" + text + """
--------------------

Return ONLY the JSON array.
"""

    answer, provider_used = generate_with_fallback(
        "Extract the questions from this question paper.",
        prompt
    )

    cleaned_response = clean_json_response(answer)

    try:
        questions = json.loads(cleaned_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Could not parse the AI response as JSON: {error}"
        )

    if not isinstance(questions, list):
        raise ValueError(
            "AI response is not a valid question list."
        )

    validated_questions = []

    for question in questions:

        if not isinstance(question, dict):
            continue

        question_number = question.get(
            "question_number",
            ""
        )

        question_text = question.get(
            "question_text",
            ""
        )

        if not question_text.strip():
            continue

        validated_questions.append(
            {
                "question_number": str(
                    question_number
                ),
                "question_text": question_text.strip()
            }
        )

    return validated_questions, provider_used
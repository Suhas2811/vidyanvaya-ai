import json
import re

from services.ai_provider import generate_with_fallback


def clean_json_response(response):
    """
    Clean an AI-generated JSON response.

    Handles:
    - Leading/trailing whitespace
    - Markdown code fences such as ```json ... ```
    - Extra text before/after the JSON
    """

    if response is None:
        return ""

    response = str(response).strip()

    if not response:
        return ""

    # Remove Markdown code fences
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


def extract_json_array(response):
    """
    Extract a JSON array from an AI response.

    This protects the application if the model returns
    additional text around the JSON.
    """

    cleaned_response = clean_json_response(response)

    if not cleaned_response:
        raise ValueError(
            "The AI returned an empty response."
        )

    start_index = cleaned_response.find("[")
    end_index = cleaned_response.rfind("]")

    if start_index == -1 or end_index == -1:
        raise ValueError(
            "Could not find a JSON array in the AI response.\n\n"
            f"AI response:\n{cleaned_response[:1500]}"
        )

    json_text = cleaned_response[
        start_index:end_index + 1
    ]

    try:
        return json.loads(json_text)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Could not parse the AI response as JSON.\n\n"
            f"Parser error: {error}\n\n"
            f"AI response:\n{cleaned_response[:1500]}"
        )


def extract_json_object(response):
    """
    Extract a JSON object from an AI response.

    This protects the application if the model returns
    additional text around the JSON object.
    """

    cleaned_response = clean_json_response(response)

    if not cleaned_response:
        raise ValueError(
            "The AI returned an empty response."
        )

    start_index = cleaned_response.find("{")
    end_index = cleaned_response.rfind("}")

    if start_index == -1 or end_index == -1:
        raise ValueError(
            "Could not find a JSON object in the AI response.\n\n"
            f"AI response:\n{cleaned_response[:1500]}"
        )

    json_text = cleaned_response[
        start_index:end_index + 1
    ]

    try:
        return json.loads(json_text)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Could not parse the AI evaluation as JSON.\n\n"
            f"Parser error: {error}\n\n"
            f"AI response:\n{cleaned_response[:1500]}"
        )


def generate_practice_test(
    academic_context,
    number_of_questions=5,
    difficulty="Medium",
    topic="All Topics"
):
    """
    Generate an exam-style practice test using the
    uploaded academic material as the primary source.

    Returns:
        questions, provider_used
    """

    topic_instruction = ""

    if topic and topic != "All Topics":
        topic_instruction = f"""
Focus the questions primarily on this topic:

{topic}
"""

    prompt = f"""
You are VidyānVaya AI, an academic exam-preparation
assistant.

Generate an exam-style practice test using ONLY the
provided academic material as the primary source.

Requirements:

1. Generate exactly {number_of_questions} questions.

2. Difficulty level:
{difficulty}

3. {topic_instruction}

4. Questions must be based on concepts, definitions,
   formulas, methods, examples, or information found
   in the academic material.

5. Do not introduce unrelated external topics.

6. Do not copy the same question repeatedly.

7. Questions should be useful for university examination
   preparation.

8. Include a mixture of appropriate question styles such
   as conceptual, descriptive, application-based, or
   numerical questions when supported by the material.

9. Do NOT provide answers.

10. Do NOT provide explanations outside the JSON.

11. Return ONLY valid JSON.

12. Do NOT use Markdown code fences.

Use exactly this structure:

[
    {{
        "question_number": 1,
        "question": "Question text",
        "difficulty": "{difficulty}"
    }}
]

Academic Material:
------------------
{academic_context}
------------------

Return ONLY the JSON array.
"""

    try:

        response, provider_used = generate_with_fallback(
            "Generate an exam-style practice test.",
            prompt
        )

        questions = extract_json_array(response)

    except Exception as error:

        raise RuntimeError(
            f"Could not generate practice questions: {error}"
        )

    if not isinstance(questions, list):

        raise ValueError(
            "AI response is not a valid question list."
        )

    validated_questions = []

    for index, question in enumerate(
        questions,
        start=1
    ):

        if not isinstance(question, dict):
            continue

        question_text = str(
            question.get(
                "question",
                ""
            )
        ).strip()

        if not question_text:
            continue

        question_number = question.get(
            "question_number",
            index
        )

        question_difficulty = str(
            question.get(
                "difficulty",
                difficulty
            )
        ).strip()

        validated_questions.append(
            {
                "question_number": question_number,
                "question": question_text,
                "difficulty": question_difficulty
            }
        )

    if not validated_questions:

        raise ValueError(
            "The AI returned no valid practice questions."
        )

    # Keep only the requested number of questions.
    validated_questions = validated_questions[
        :number_of_questions
    ]

    return (
        validated_questions,
        provider_used
    )


def evaluate_answer(
    question,
    student_answer,
    academic_context
):
    """
    Evaluate a student's answer using the uploaded
    academic material as the primary source.

    Returns:
        evaluation, provider_used
    """

    prompt = f"""
You are VidyānVaya AI, an academic answer evaluator.

Evaluate the student's answer against the question
and the provided academic material.

Question:
------------------
{question}
------------------

Student Answer:
------------------
{student_answer}
------------------

Academic Material:
------------------
{academic_context}
------------------

Evaluation requirements:

1. Evaluate the answer based primarily on the provided
   academic material.

2. Do not penalize the student for wording differences
   when the underlying concept is correct.

3. Identify whether the answer is:
   - Correct
   - Partially Correct
   - Incorrect

4. Explain what the student did correctly.

5. Explain what is missing or incorrect.

6. Provide a concise ideal answer based on the
   academic material.

7. Give a score from 0 to 10.

8. Do not introduce unrelated external information.

9. Return ONLY valid JSON.

10. Do NOT use Markdown code fences.

Use exactly this structure:

{{
    "result": "Correct",
    "score": 8,
    "feedback": "The answer correctly explains...",
    "missing_points": [
        "Point that was missing"
    ],
    "ideal_answer": "A concise ideal answer based on the material."
}}

Return ONLY the JSON object.
"""

    try:

        response, provider_used = generate_with_fallback(
            "Evaluate the student's academic answer.",
            prompt
        )

        evaluation = extract_json_object(response)

    except Exception as error:

        raise RuntimeError(
            f"Could not evaluate the answer: {error}"
        )

    if not isinstance(evaluation, dict):

        raise ValueError(
            "AI response is not a valid evaluation object."
        )

    result = str(
        evaluation.get(
            "result",
            ""
        )
    ).strip()

    feedback = str(
        evaluation.get(
            "feedback",
            ""
        )
    ).strip()

    ideal_answer = str(
        evaluation.get(
            "ideal_answer",
            ""
        )
    ).strip()

    if not result:
        result = "Not Evaluated"

    if not feedback:
        feedback = (
            "No detailed feedback was generated."
        )

    if not ideal_answer:
        ideal_answer = (
            "No ideal answer was generated."
        )

    try:

        score = float(
            evaluation.get(
                "score",
                0
            )
        )

    except (TypeError, ValueError):

        score = 0

    # Keep score between 0 and 10.
    score = max(
        0,
        min(
            10,
            score
        )
    )

    missing_points = evaluation.get(
        "missing_points",
        []
    )

    if not isinstance(
        missing_points,
        list
    ):

        missing_points = []

    missing_points = [
        str(point).strip()
        for point in missing_points
        if str(point).strip()
    ]

    validated_evaluation = {
        "result": result,
        "score": score,
        "feedback": feedback,
        "missing_points": missing_points,
        "ideal_answer": ideal_answer
    }

    return (
        validated_evaluation,
        provider_used
    )
import json
import re

from services.ai_provider import generate_with_fallback


# ==================================================
# JSON HELPERS
# ==================================================

def _clean_json_response(response_text):
    """
    Remove Markdown code fences and surrounding whitespace.
    """

    text = str(response_text or "").strip()

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
    """
    Extract a JSON array from an AI response.
    """

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
    """
    Validate and normalize extracted questions.
    """

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
            "No usable questions were returned."
        )

    # Always use stable sequential numbering.
    for index, question in enumerate(
        normalised,
        start=1
    ):
        question["question_number"] = str(index)

    return normalised


# ==================================================
# LOCAL QUESTION EXTRACTION
# ==================================================

def _extract_questions_locally(question_paper_text):
    """
    Extract numbered questions locally without using an LLM.

    This is intentionally the first extraction method because
    examination papers normally contain clearly numbered questions.

    Examples detected:

        1. Explain process management.
        2) What is a thread?
        Q3. Explain scheduling.
        Q4) Describe paging.
        Question 5: Explain deadlock.

    Sub-parts such as:

        (a)
        (b)
        (c)

    remain attached to their parent question.
    """

    text = str(
        question_paper_text or ""
    ).replace("\r\n", "\n").replace("\r", "\n").strip()

    if not text:
        return []

    lines = text.split("\n")

    questions = []
    current_question = None

    # Main question markers.
    #
    # Matches:
    #   1. Question
    #   1) Question
    #   1: Question
    #   Q1. Question
    #   Q.1 Question
    #   Question 1: Question
    #   Question 1. Question
    #
    question_pattern = re.compile(
        r"^\s*"
        r"(?:"
        r"Q(?:uestion)?\s*\.?\s*"
        r")?"
        r"(\d{1,3})"
        r"\s*[\.\):\-]\s+"
        r"(.+?)"
        r"\s*$",
        re.IGNORECASE
    )

    # "Question 1:" / "Question No. 1:"
    question_word_pattern = re.compile(
        r"^\s*"
        r"(?:Question|Ques\.?|Q)"
        r"\s*(?:No\.?\s*)?"
        r"(\d{1,3})"
        r"\s*[\.\):\-]\s*"
        r"(.*?)"
        r"\s*$",
        re.IGNORECASE
    )

    # Number-only line followed by question text.
    # Useful for OCR output such as:
    #
    # 1
    # Explain process management.
    #
    number_only_pattern = re.compile(
        r"^\s*(\d{1,3})\s*$"
    )

    pending_number = None

    def flush_current_question():
        nonlocal current_question

        if current_question is None:
            return

        question_text = " ".join(
            part.strip()
            for part in current_question["parts"]
            if part.strip()
        ).strip()

        if question_text:
            questions.append(
                {
                    "question_number": str(
                        current_question["number"]
                    ),
                    "question_text": question_text,
                }
            )

        current_question = None

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        # --------------------------------------------------
        # Handle a number-only line.
        # --------------------------------------------------

        number_only_match = number_only_pattern.match(line)

        if number_only_match:
            pending_number = number_only_match.group(1)
            continue

        # --------------------------------------------------
        # Handle "Question 1: ..."
        # --------------------------------------------------

        word_match = question_word_pattern.match(line)

        if word_match:
            flush_current_question()

            number = word_match.group(1)
            question_text = word_match.group(2).strip()

            current_question = {
                "number": number,
                "parts": []
            }

            if question_text:
                current_question["parts"].append(
                    question_text
                )

            pending_number = None
            continue

        # --------------------------------------------------
        # Handle "1. ...", "1) ...", "Q1. ..."
        # --------------------------------------------------

        normal_match = question_pattern.match(line)

        if normal_match:

            # Avoid treating "1.5" style numeric content as
            # a new question.
            number = normal_match.group(1)
            question_text = normal_match.group(2).strip()

            flush_current_question()

            current_question = {
                "number": number,
                "parts": []
            }

            if question_text:
                current_question["parts"].append(
                    question_text
                )

            pending_number = None
            continue

        # --------------------------------------------------
        # If a number-only question marker was found earlier,
        # this line becomes its question text.
        # --------------------------------------------------

        if pending_number is not None:

            flush_current_question()

            current_question = {
                "number": pending_number,
                "parts": [line]
            }

            pending_number = None
            continue

        # --------------------------------------------------
        # Continuation line.
        #
        # This keeps:
        # (a) ...
        # (b) ...
        # and wrapped question text together.
        # --------------------------------------------------

        if current_question is not None:

            current_question["parts"].append(
                line
            )

    # Flush final question.
    flush_current_question()

    # ------------------------------------------------------
    # Remove obvious false positives.
    # ------------------------------------------------------

    cleaned_questions = []

    for question in questions:

        question_text = question[
            "question_text"
        ].strip()

        if len(question_text) < 5:
            continue

        # Ignore lines that look like page numbers.
        if question_text.isdigit():
            continue

        cleaned_questions.append(
            {
                "question_number": str(
                    len(cleaned_questions) + 1
                ),
                "question_text": question_text,
            }
        )

    return cleaned_questions


# ==================================================
# AI FALLBACK EXTRACTION
# ==================================================

def _extract_questions_with_ai(question_paper_text):
    """
    Use the configured AI provider only when local extraction
    cannot confidently identify the question structure.
    """

    text = str(
        question_paper_text or ""
    ).strip()

    if not text:
        raise ValueError(
            "Question paper text is empty."
        )

    # Keep the AI input bounded.
    max_input_chars = 18000

    if len(text) > max_input_chars:
        text = text[:max_input_chars]

    prompt = f"""
Extract every individual examination question from the question paper below.

Return ONLY a JSON array.

Each item must contain exactly:
- "question_number"
- "question_text"

Rules:
1. Preserve the original wording as closely as possible.
2. Keep sub-parts such as (a), (b), and (c) together with their parent question.
3. Do not create answers.
4. Do not create explanations.
5. Do not create summaries.
6. Do not duplicate questions.
7. Do not invent missing text.
8. Return valid JSON only.

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

    return questions, provider_used


# ==================================================
# MAIN QUESTION EXTRACTION
# ==================================================

def extract_questions(question_paper_text):
    """
    Extract examination questions.

    Strategy:

    1. Try local extraction first.
    2. If the paper has a clear numbered structure,
       return immediately without using an AI model.
    3. If local extraction is not reliable, use the
       existing Gemini/OpenAI/Ollama fallback system.

    This prevents unnecessary AI calls and greatly
    reduces Question Bank extraction time.
    """

    text = str(
        question_paper_text or ""
    ).strip()

    if not text:
        raise ValueError(
            "Question paper text is empty."
        )

    # ==================================================
    # STEP 1 — LOCAL EXTRACTION
    # ==================================================

    local_questions = _extract_questions_locally(
        text
    )

    # ==================================================
    # STEP 2 — CONFIDENCE CHECK
    # ==================================================

    #
    # A normal university question paper generally has
    # at least two numbered questions.
    #
    # If local extraction finds a reasonable number of
    # questions, there is no reason to call an LLM.
    #

    if len(local_questions) >= 2:

        return (
            local_questions,
            "local"
        )

    # ==================================================
    # STEP 3 — AI FALLBACK
    # ==================================================

    return _extract_questions_with_ai(
        text
    )
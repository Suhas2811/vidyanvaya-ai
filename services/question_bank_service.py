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
# TEXT CLEANING
# ==================================================

def _clean_line(line):
    """
    Clean common PDF/OCR formatting noise while preserving
    the actual question wording.
    """

    line = str(line).strip()

    if not line:
        return ""

    # Normalize repeated whitespace.
    line = re.sub(
        r"\s+",
        " ",
        line
    )

    # Remove trailing examination metadata such as:
    # 10 L4 CO1
    # 12 L2 CO3
    line = re.sub(
        r"\s+\d{1,3}\s+L\d+\s+CO\d+\s*$",
        "",
        line,
        flags=re.IGNORECASE
    )

    # Remove metadata at the beginning.
    line = re.sub(
        r"^\d{1,3}\s+L\d+\s+CO\d+\s+",
        "",
        line,
        flags=re.IGNORECASE
    )

    # Sometimes OCR produces:
    # L4 CO1 b) Explain...
    #
    # Remove the metadata but preserve the sub-question.
    line = re.sub(
        r"^L\d+\s+CO\d+\s+",
        "",
        line,
        flags=re.IGNORECASE
    )

    return line.strip()


def _is_metadata_line(line):
    """
    Identify lines that belong to the question-paper layout
    rather than an actual question.
    """

    if not line:
        return True

    normalized = re.sub(
        r"\s+",
        " ",
        line
    ).strip()

    metadata_patterns = [
        r"^USN$",
        r"^PTO$",
        r"^OR$",
        r"^Course\s*:",
        r"^Course Code\s*:",
        r"^Max Marks\s*:",
        r"^Duration\s*:",
        r"^Note\s*:",
        r"^DAYANANDA SAGAR",
        r"^Fifth Semester",
        r"^Semester End Examination",
        r"^An Autonomous Institute",
        r"^Module\s*[-–—]\s*\d+",
        r"^Module\s+\d+",
        r"^Marks\s+BL\s+CO$",
    ]

    for pattern in metadata_patterns:

        if re.search(
            pattern,
            normalized,
            flags=re.IGNORECASE
        ):
            return True

    # Example:
    # 10 L4 CO1
    # 12 L2 CO3
    if re.fullmatch(
        r"\d{1,3}\s+L\d+\s+CO\d+",
        normalized,
        flags=re.IGNORECASE
    ):
        return True

    # IMPORTANT:
    #
    # Do NOT treat standalone numbers as metadata here.
    #
    # A university question paper may contain:
    #
    # 1
    # 2
    # 3
    #
    # and those are actual question numbers.
    #
    # Number detection happens BEFORE this function is
    # called anyway, but keeping standalone numbers out
    # of this filter makes the behaviour safer.
    #
    return False


# ==================================================
# QUESTION PATTERN HELPERS
# ==================================================

def _match_subpart(line):
    """
    Detect sub-question formats:

        a)
        b)
        c)

        (a)
        (b)
        (c)
    """

    match = re.match(
        r"^\s*(\([a-z]\)|[a-z]\))\s*(.*)$",
        line,
        flags=re.IGNORECASE
    )

    if not match:
        return None

    marker = match.group(1)
    text = match.group(2).strip()

    return marker, text


def _match_numbered_question(line):
    """
    Detect common university question formats.

    Supported examples:

        1
        1.
        1)
        1: Explain...
        Q1
        Q1.
        Q1:
        Question 1
        Question 1:
        1 a) Explain...
        1. a) Explain...
    """

    # --------------------------------------------------
    # Question number
    # --------------------------------------------------

    match = re.match(
        r"^\s*(?:Q(?:uestion)?\s*)?(\d{1,2})"
        r"(?:\s*[\.:)])?"
        r"(?:\s+(.+))?\s*$",
        line,
        flags=re.IGNORECASE
    )

    if not match:
        return None

    number = int(
        match.group(1)
    )

    remainder = (
        match.group(2) or ""
    ).strip()

    # Avoid interpreting random large numbers as
    # question numbers.
    if number < 1 or number > 50:
        return None

    # --------------------------------------------------
    # Inline sub-question
    #
    # Example:
    #
    # 1 a) Explain Boolean retrieval.
    # --------------------------------------------------

    subpart = _match_subpart(
        remainder
    )

    if subpart:

        marker, text = subpart

        return {
            "number": number,
            "subpart": marker,
            "text": text
        }

    # --------------------------------------------------
    # Metadata after question number
    #
    # Example:
    #
    # 10 L4 CO1
    #
    # This is not a question.
    # --------------------------------------------------

    if re.fullmatch(
        r"L\d+\s+CO\d+",
        remainder,
        flags=re.IGNORECASE
    ):
        return None

    # --------------------------------------------------
    # Number-only question
    #
    # Example:
    #
    # 1
    # 2
    # 3
    #
    # These are valid question headers.
    # --------------------------------------------------

    if not remainder:

        return {
            "number": number,
            "subpart": None,
            "text": ""
        }

    # --------------------------------------------------
    # Numbered question with text
    # --------------------------------------------------

    return {
        "number": number,
        "subpart": None,
        "text": remainder
    }


# ==================================================
# LOCAL QUESTION EXTRACTION
# ==================================================

def _extract_questions_locally(question_paper_text):
    """
    Extract questions using deterministic rules.

    This is preferred for normal university question papers
    because it is fast and avoids unnecessary LLM calls.

    The parser:

    - detects main question numbers
    - detects (a), (b), (c) subparts
    - keeps continuation lines
    - ignores OR
    - ignores marks / BL / CO metadata
    - ignores module headings
    - ignores examination instructions
    - preserves numerical data belonging to questions
    """

    text = str(
        question_paper_text or ""
    ).strip()

    if not text:
        return []

    # Normalize line endings.
    text = text.replace(
        "\r\n",
        "\n"
    ).replace(
        "\r",
        "\n"
    )

    raw_lines = text.split(
        "\n"
    )

    # Clean individual lines.
    lines = []

    for raw_line in raw_lines:

        cleaned = _clean_line(
            raw_line
        )

        if cleaned:
            lines.append(
                cleaned
            )

    questions = []

    current_question = None
    current_part = None

    # ==================================================
    # IMPORTANT PARSING ORDER
    # ==================================================
    #
    # 1. Numbered question
    # 2. Sub-question
    # 3. OR
    # 4. Metadata
    # 5. Continuation text
    #
    # Numbered questions MUST be detected before metadata.
    # ==================================================

    for line in lines:

        # --------------------------------------------------
        # 1. Detect numbered question FIRST
        # --------------------------------------------------

        numbered = _match_numbered_question(
            line
        )

        if numbered:

            number = numbered[
                "number"
            ]

            subpart = numbered[
                "subpart"
            ]

            question_text = numbered[
                "text"
            ]

            # Find an existing question with this number.
            existing = None

            for question in questions:

                if (
                    question["question_number"]
                    == str(number)
                ):
                    existing = question
                    break

            # Create a new question if necessary.
            if existing is None:

                current_question = {
                    "question_number": str(number),
                    "parts": []
                }

                questions.append(
                    current_question
                )

            else:

                current_question = existing

            # --------------------------------------------------
            # Numbered line containing a subpart
            #
            # Example:
            #
            # 1 a) Analyze...
            # --------------------------------------------------

            if subpart:

                part_text = (
                    f"{subpart} {question_text}"
                    if question_text
                    else subpart
                ).strip()

                current_question[
                    "parts"
                ].append(
                    part_text
                )

                current_part = (
                    len(
                        current_question[
                            "parts"
                        ]
                    ) - 1
                )

            # --------------------------------------------------
            # Numbered line containing question text
            # --------------------------------------------------

            elif question_text:

                current_question[
                    "parts"
                ].append(
                    question_text
                )

                current_part = (
                    len(
                        current_question[
                            "parts"
                        ]
                    ) - 1
                )

            # --------------------------------------------------
            # Number-only line
            #
            # Example:
            #
            # 1
            #
            # The actual question comes on the next line.
            # --------------------------------------------------

            else:

                current_part = None

            continue

        # --------------------------------------------------
        # 2. Detect sub-question
        #
        # Example:
        #
        # a) Analyze...
        # b) Explain...
        # --------------------------------------------------

        subpart = _match_subpart(
            line
        )

        if (
            subpart
            and current_question
        ):

            marker, question_text = subpart

            part_text = (
                f"{marker} {question_text}"
                if question_text
                else marker
            ).strip()

            current_question[
                "parts"
            ].append(
                part_text
            )

            current_part = (
                len(
                    current_question[
                        "parts"
                    ]
                ) - 1
            )

            continue

        # --------------------------------------------------
        # 3. Ignore OR
        # --------------------------------------------------

        if re.fullmatch(
            r"OR",
            line,
            flags=re.IGNORECASE
        ):
            current_part = None
            continue

        # --------------------------------------------------
        # 4. Ignore metadata
        # --------------------------------------------------

        if _is_metadata_line(
            line
        ):
            continue

        # --------------------------------------------------
        # 5. Continuation line
        #
        # If the current question has a subpart,
        # append the line to that subpart.
        # --------------------------------------------------

        if (
            current_question
            and current_part is not None
            and current_question[
                "parts"
            ]
        ):

            current_question[
                "parts"
            ][current_part] += (
                " " + line
            )


    # ==================================================
    # CONVERT INTERNAL STRUCTURE
    # ==================================================

    normalised = []

    for question in questions:

        parts = [
            part.strip()
            for part in question[
                "parts"
            ]
            if part.strip()
        ]

        if not parts:
            continue

        question_text = "\n".join(
            parts
        ).strip()

        normalised.append(
            {
                "question_number": question[
                    "question_number"
                ],
                "question_text": question_text
            }
        )

    # ==================================================
    # REMOVE DUPLICATE QUESTION NUMBERS
    # ==================================================

    final_questions = []

    seen_numbers = set()

    for question in normalised:

        number = question[
            "question_number"
        ]

        if number in seen_numbers:
            continue

        seen_numbers.add(
            number
        )

        final_questions.append(
            question
        )

    return final_questions


# ==================================================
# QUESTION VALIDATION
# ==================================================

def _normalise_questions(
    questions
):
    """
    Validate and normalize AI-generated questions.
    """

    if not isinstance(
        questions,
        list
    ):
        raise ValueError(
            "AI returned an invalid question list."
        )

    normalised = []

    for index, item in enumerate(
        questions,
        start=1
    ):

        if not isinstance(
            item,
            dict
        ):
            continue

        question_text = str(
            item.get(
                "question_text",
                item.get(
                    "question",
                    ""
                )
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
                "question_text": question_text
            }
        )

    if not normalised:

        raise ValueError(
            "No usable questions were returned by the AI."
        )

    return normalised


# ==================================================
# AI QUESTION EXTRACTION
# ==================================================

def _extract_questions_with_ai(
    question_paper_text
):
    """
    AI fallback for question papers whose structure
    cannot be reliably detected locally.
    """

    text = str(
        question_paper_text or ""
    ).strip()

    if not text:
        raise ValueError(
            "Question paper text is empty."
        )

    # Keep the input bounded.
    max_input_chars = 18000

    if len(text) > max_input_chars:

        text = text[
            :max_input_chars
        ]

    prompt = f"""
Extract every individual examination question from the
question paper below.

Return ONLY a JSON array.

Each item must contain exactly:

- "question_number"
- "question_text"

Rules:

1. Preserve the original question wording as closely as possible.

2. Keep sub-parts such as (a), (b), and (c) together with
   their parent question.

3. Do NOT treat marks, BL, CO, module headings, duration,
   examination instructions, OR, PTO, page numbers, or
   university information as questions.

4. Do NOT create explanations or answers.

5. Do NOT invent missing text.

6. Do NOT split numerical data belonging to a question
   into separate questions.

7. Preserve the question numbers from the paper.

8. Keep each numbered examination question as one item.

QUESTION PAPER:

{text}
"""

    response_text, provider_used = (
        generate_with_fallback(
            prompt,
            ""
        )
    )

    questions = _extract_json_array(
        response_text
    )

    questions = _normalise_questions(
        questions
    )

    return (
        questions,
        provider_used
    )


# ==================================================
# MAIN EXTRACTION FUNCTION
# ==================================================

def extract_questions(
    question_paper_text
):
    """
    Extract individual questions from a question paper.

    Strategy:

    1. Try deterministic local extraction first.
    2. Validate the result.
    3. If the structure cannot be reliably identified,
       fall back to the configured AI providers.

    Returns:

        (
            questions,
            provider_used
        )
    """

    text = str(
        question_paper_text or ""
    ).strip()

    if not text:

        raise ValueError(
            "Question paper text is empty."
        )

    # ==================================================
    # LOCAL EXTRACTION
    # ==================================================

    local_questions = (
        _extract_questions_locally(
            text
        )
    )

    # ==================================================
    # LOCAL RESULT VALIDATION
    # ==================================================

    if len(local_questions) >= 2:

        # The local parser successfully found
        # a meaningful set of questions.
        #
        # Do NOT call Gemini unnecessarily.

        return (
            local_questions,
            "local"
        )

    # ==================================================
    # AI FALLBACK
    # ==================================================

    return _extract_questions_with_ai(
        text
    )
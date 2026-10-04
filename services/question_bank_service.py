import json
import re

from services.ai_provider import generate_with_fallback


# ============================================================
# JSON HELPERS
# ============================================================

def _clean_json_response(response_text):
    text = str(response_text or "").strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
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


# ============================================================
# LINE CLEANING
# ============================================================

def _clean_line(line):
    """
    Clean a single extracted PDF line.

    Important:
    We do NOT remove question numbers here.
    """

    line = str(line or "").strip()

    if not line:
        return ""

    # Normalize whitespace.
    line = re.sub(
        r"[ \t]+",
        " ",
        line
    )

    return line.strip()


# ============================================================
# METADATA DETECTION
# ============================================================

def _is_metadata_line(line):
    """
    Detect university examination metadata.

    Question numbers themselves are NOT metadata.
    """

    line = str(line or "").strip()

    if not line:
        return True

    # Common document/examination metadata.
    metadata_patterns = [
        r"^USN$",
        r"^PTO$",
        r"^Course\s*:",
        r"^Course Code\s*:",
        r"^Max Marks\s*:",
        r"^Duration\s*:",
        r"^Note\s*:",
        r"^DAYANANDA SAGAR",
        r"^An Autonomous Institute",
        r"^Fifth Semester",
        r"^Semester End Examination",
        r"^Module\s*[-–—]?\s*\d+",
        r"^Marks\s+BL\s+CO$",
        r"^OR$",
        r"^\*+$",
    ]

    for pattern in metadata_patterns:
        if re.search(
            pattern,
            line,
            flags=re.IGNORECASE
        ):
            return True

    # Examples:
    # 10 L4 CO1
    # 12 L3 CO2
    # 8 L3 CO3
    if re.fullmatch(
        r"\d{1,3}\s+L\d+\s+CO\d+",
        line,
        flags=re.IGNORECASE
    ):
        return True

    return False


# ============================================================
# QUESTION START DETECTION
# ============================================================

def _match_question_start(line):
    """
    Detect a main question.

    Handles:

        1
        1.
        1)
        1:
        1 a)
        1. a)
        Q1
        Q1.
        Question 1

    Returns:

        {
            "number": "1",
            "subpart": "a)",
            "text": "..."
        }

    or None.
    """

    line = str(line or "").strip()

    if not line:
        return None

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # We require the question number to be at the beginning.
    # --------------------------------------------------------

    match = re.match(
        r"^(?:Q(?:uestion)?\s*)?"
        r"(\d{1,2})"
        r"(?:[.):])?"
        r"(?:\s+(.+))?$",
        line,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    number = int(
        match.group(1)
    )

    # University papers normally have a small number
    # of questions. Avoid interpreting arbitrary numbers
    # inside text as question numbers.
    if number < 1 or number > 50:
        return None

    remainder = (
        match.group(2) or ""
    ).strip()

    # --------------------------------------------------------
    # Metadata such as:
    #
    # 10 L4 CO1
    #
    # must NOT become a question.
    # --------------------------------------------------------

    if re.fullmatch(
        r"L\d+\s+CO\d+",
        remainder,
        flags=re.IGNORECASE,
    ):
        return None

    # --------------------------------------------------------
    # Detect inline subpart.
    #
    # Example:
    #
    # 1 a) Analyze...
    # --------------------------------------------------------

    subpart_match = re.match(
        r"^(\([a-z]\)|[a-z]\))\s*(.*)$",
        remainder,
        flags=re.IGNORECASE,
    )

    if subpart_match:

        return {
            "number": str(number),
            "subpart": subpart_match.group(1),
            "text": subpart_match.group(2).strip(),
        }

    # --------------------------------------------------------
    # Number-only question.
    #
    # Example:
    #
    # 1
    #
    # followed by:
    #
    # a) ...
    # --------------------------------------------------------

    if not remainder:

        return {
            "number": str(number),
            "subpart": None,
            "text": "",
        }

    # --------------------------------------------------------
    # Numbered question with text but no subpart.
    # --------------------------------------------------------

    return {
        "number": str(number),
        "subpart": None,
        "text": remainder,
    }


# ============================================================
# SUBPART DETECTION
# ============================================================

def _match_subpart(line):
    """
    Detect:

        a) ...
        b) ...
        c) ...

        (a) ...
        (b) ...
        (c) ...
    """

    line = str(line or "").strip()

    match = re.match(
        r"^(\([a-z]\)|[a-z]\))\s*(.*)$",
        line,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return (
        match.group(1),
        match.group(2).strip(),
    )


# ============================================================
# LOCAL QUESTION EXTRACTION
# ============================================================

def _extract_questions_locally(question_paper_text):
    """
    Deterministically extract questions from a university
    question paper.

    This parser is intentionally local-first.

    It supports papers where the structure looks like:

        1 a) Question...
        10 L4 CO1
        b) Question...
        10 L3 CO1
        OR
        2 a) Question...

    It ignores examination metadata and keeps continuation
    text and numerical data inside the correct question.
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

    lines = []

    for raw_line in raw_lines:

        cleaned = _clean_line(
            raw_line
        )

        if cleaned:
            lines.append(
                cleaned
            )

    # --------------------------------------------------------
    # Internal representation:
    #
    # {
    #     "number": "1",
    #     "parts": [
    #         "a) ...",
    #         "b) ..."
    #     ]
    # }
    # --------------------------------------------------------

    question_map = {}

    current_question = None
    current_part_index = None

    for line in lines:

        # ====================================================
        # 1. MAIN QUESTION DETECTION
        #
        # THIS MUST COME FIRST.
        # ====================================================

        question_start = _match_question_start(
            line
        )

        if question_start is not None:

            number = question_start[
                "number"
            ]

            subpart = question_start[
                "subpart"
            ]

            question_text = question_start[
                "text"
            ]

            # Create question if not already present.
            if number not in question_map:

                question_map[number] = {
                    "question_number": number,
                    "parts": [],
                }

            current_question = question_map[
                number
            ]

            # ------------------------------------------------
            # Inline subpart.
            #
            # Example:
            #
            # 1 a) Analyze...
            # ------------------------------------------------

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

                current_part_index = (
                    len(
                        current_question[
                            "parts"
                        ]
                    ) - 1
                )

            # ------------------------------------------------
            # Numbered question containing text.
            # ------------------------------------------------

            elif question_text:

                current_question[
                    "parts"
                ].append(
                    question_text
                )

                current_part_index = (
                    len(
                        current_question[
                            "parts"
                        ]
                    ) - 1
                )

            # ------------------------------------------------
            # Number-only question.
            #
            # The next a)/b)/text line belongs to it.
            # ------------------------------------------------

            else:

                current_part_index = None

            continue

        # ====================================================
        # 2. SUBPART DETECTION
        # ====================================================

        subpart = _match_subpart(
            line
        )

        if (
            subpart is not None
            and current_question is not None
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

            current_part_index = (
                len(
                    current_question[
                        "parts"
                    ]
                ) - 1
            )

            continue

        # ====================================================
        # 3. OR
        # ====================================================

        if re.fullmatch(
            r"OR",
            line,
            flags=re.IGNORECASE,
        ):

            # OR is a separator, not a question.
            #
            # Do NOT destroy current_question because the next
            # numbered question should still be detected.
            current_part_index = None

            continue

        # ====================================================
        # 4. METADATA
        # ====================================================

        if _is_metadata_line(
            line
        ):

            continue

        # ====================================================
        # 5. CONTINUATION TEXT
        # ====================================================

        if (
            current_question is not None
            and current_part_index is not None
        ):

            current_question[
                "parts"
            ][current_part_index] += (
                " " + line
            )


    # ========================================================
    # BUILD FINAL LIST
    # ========================================================

    questions = []

    # Sort numerically:
    #
    # 1, 2, 3 ... 10
    #
    # instead of:
    #
    # 1, 10, 2 ...
    # ========================================================

    sorted_questions = sorted(
        question_map.values(),
        key=lambda item: int(
            item["question_number"]
        ),
    )

    for question in sorted_questions:

        parts = [
            part.strip()
            for part in question["parts"]
            if part.strip()
        ]

        if not parts:
            continue

        question_text = "\n".join(
            parts
        ).strip()

        questions.append(
            {
                "question_number": question[
                    "question_number"
                ],
                "question_text": question_text,
            }
        )

    return questions


# ============================================================
# LOCAL VALIDATION
# ============================================================

def _is_valid_local_result(
    questions,
    original_text,
):
    """
    Validate whether local extraction produced a useful
    question bank.

    For a normal university paper, we expect at least
    two numbered questions.

    Also reject obvious metadata-only results.
    """

    if not isinstance(
        questions,
        list,
    ):
        return False

    if len(questions) < 2:
        return False

    valid_questions = 0

    for question in questions:

        number = str(
            question.get(
                "question_number",
                "",
            )
        ).strip()

        text = str(
            question.get(
                "question_text",
                "",
            )
        ).strip()

        if not number or not text:
            continue

        # Reject obvious metadata.
        if re.search(
            r"Duration\s*:",
            text,
            flags=re.IGNORECASE,
        ):
            continue

        if re.search(
            r"Max Marks\s*:",
            text,
            flags=re.IGNORECASE,
        ):
            continue

        if re.search(
            r"DAYANANDA SAGAR",
            text,
            flags=re.IGNORECASE,
        ):
            continue

        valid_questions += 1

    return valid_questions >= 2


# ============================================================
# AI FALLBACK
# ============================================================

def _extract_questions_with_ai(
    question_paper_text
):
    """
    AI fallback for unusual question-paper layouts.
    """

    text = str(
        question_paper_text or ""
    ).strip()

    if not text:
        raise ValueError(
            "Question paper text is empty."
        )

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

1. Preserve the original wording as closely as possible.

2. Preserve the original question numbers.

3. Keep sub-parts such as (a), (b), and (c) together
   inside their parent numbered question.

4. Do NOT treat Duration, Max Marks, USN, Course,
   Course Code, Module, Marks, BL, CO, PTO, OR,
   university information, or page numbers as questions.

5. Do NOT create questions that are not present.

6. Do NOT split numerical data belonging to a question
   into separate questions.

7. Preserve formulas, values, examples, and numerical
   information belonging to a question.

8. Return one object for each numbered main question.

QUESTION PAPER:

{text}
"""

    response_text, provider_used = (
        generate_with_fallback(
            prompt,
            "",
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
        provider_used,
    )


# ============================================================
# AI RESULT NORMALIZATION
# ============================================================

def _normalise_questions(
    questions
):
    """
    Validate and normalize AI-generated questions.
    """

    if not isinstance(
        questions,
        list,
    ):
        raise ValueError(
            "AI returned an invalid question list."
        )

    normalised = []

    for index, item in enumerate(
        questions,
        start=1,
    ):

        if not isinstance(
            item,
            dict,
        ):
            continue

        question_text = str(
            item.get(
                "question_text",
                item.get(
                    "question",
                    "",
                ),
            )
        ).strip()

        if not question_text:
            continue

        question_number = str(
            item.get(
                "question_number",
                index,
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


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def extract_questions(
    question_paper_text
):
    """
    Main Question Bank extraction function.

    Strategy:

        PDF text
             ↓
        Local parser
             ↓
        Valid?
        ↙     ↘
      YES      NO
       ↓        ↓
     Local     AI fallback

    Local extraction is preferred so that ordinary
    university papers do not depend on an LLM.
    """

    text = str(
        question_paper_text or ""
    ).strip()

    if not text:

        raise ValueError(
            "Question paper text is empty."
        )

    # --------------------------------------------------------
    # LOCAL FIRST
    # --------------------------------------------------------

    local_questions = (
        _extract_questions_locally(
            text
        )
    )

    # --------------------------------------------------------
    # VALIDATE LOCAL RESULT
    # --------------------------------------------------------

    if _is_valid_local_result(
        local_questions,
        text,
    ):

        return (
            local_questions,
            "local",
        )

    # --------------------------------------------------------
    # AI FALLBACK
    # --------------------------------------------------------

    return _extract_questions_with_ai(
        text
    )
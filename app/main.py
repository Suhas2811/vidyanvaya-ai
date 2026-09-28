import sys
import time
import json
from io import BytesIO
from pathlib import Path

import streamlit as st


# ==================================================
# PROJECT PATH
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ==================================================
# DOCUMENT PROCESSING
# ==================================================

from document_processing.pdf_processor import (
    extract_text_from_pdf
)

from document_processing.docx_processor import (
    extract_text_from_docx
)

from document_processing.pptx_processor import (
    extract_text_from_pptx
)


# ==================================================
# RAG
# ==================================================

from rag.chunking import chunk_text

from rag.embeddings import create_embeddings

from rag.vector_store import (
    store_embeddings,
    get_collection_count,
    get_document_names,
    create_file_id
)

from rag.retrieval import (
    retrieve_relevant_chunks
)


# ==================================================
# AI / SERVICES
# ==================================================

from services.ai_provider import (
    generate_with_fallback
)

from services.question_bank_service import (
    extract_questions
)

from services.exam_prep_service import (
    generate_practice_test,
    evaluate_answer
)

from services.performance_service import (
    get_performance_summary
)


# ==================================================
# STREAMLIT CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="VidyānVaya AI",
    page_icon="📚",
    layout="wide"
)


# ==================================================
# SESSION STATE INITIALIZATION
# ==================================================

if "uploaded_files_data" not in st.session_state:
    st.session_state["uploaded_files_data"] = []

if "extracted_questions" not in st.session_state:
    st.session_state["extracted_questions"] = []

if "question_bank_provider" not in st.session_state:
    st.session_state["question_bank_provider"] = "unknown"

if "question_bank_source" not in st.session_state:
    st.session_state["question_bank_source"] = ""

if "exam_prep_questions" not in st.session_state:
    st.session_state["exam_prep_questions"] = []

if "exam_prep_provider" not in st.session_state:
    st.session_state["exam_prep_provider"] = "unknown"

if "exam_prep_document" not in st.session_state:
    st.session_state["exam_prep_document"] = ""

if "exam_prep_topic" not in st.session_state:
    st.session_state["exam_prep_topic"] = ""

if "exam_prep_difficulty" not in st.session_state:
    st.session_state["exam_prep_difficulty"] = "Medium"

if "exam_prep_context" not in st.session_state:
    st.session_state["exam_prep_context"] = ""

if "exam_prep_source_chunks" not in st.session_state:
    st.session_state["exam_prep_source_chunks"] = []

if "exam_prep_results" not in st.session_state:
    st.session_state["exam_prep_results"] = []

if "exam_prep_total_score" not in st.session_state:
    st.session_state["exam_prep_total_score"] = 0

if "performance_history" not in st.session_state:
    st.session_state["performance_history"] = []


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def save_uploaded_files(uploaded_files):
    """
    Store uploaded file bytes in session state so that
    the files remain available across navigation sections.
    """

    stored_files = []

    for file in uploaded_files:
        stored_files.append(
            {
                "name": file.name,
                "bytes": file.getvalue(),
            }
        )

    st.session_state["uploaded_files_data"] = stored_files


def get_uploaded_file_names():
    """
    Return names of files currently stored in session state.
    """

    return [
        file["name"]
        for file in st.session_state["uploaded_files_data"]
    ]


def get_uploaded_pdf_names():
    """
    Return uploaded PDF file names.
    """

    return [
        file["name"]
        for file in st.session_state["uploaded_files_data"]
        if file["name"].lower().endswith(".pdf")
    ]


def get_uploaded_file_bytes(file_name):
    """
    Return bytes for a stored uploaded file.
    """

    for file in st.session_state["uploaded_files_data"]:
        if file["name"] == file_name:
            return file["bytes"]

    return None


def create_file_object(file_name):
    """
    Create a BytesIO object from a stored uploaded file.
    """

    file_bytes = get_uploaded_file_bytes(file_name)

    if file_bytes is None:
        return None

    file_object = BytesIO(file_bytes)
    file_object.name = file_name

    return file_object


def process_single_document(file_name, file_bytes):
    """
    Process one academic document and store its embeddings.
    """

    file = BytesIO(file_bytes)
    file.name = file_name

    extracted_text = ""

    if file_name.lower().endswith(".pdf"):

        file.seek(0)

        pages = extract_text_from_pdf(file)

        extracted_text = "\n".join(
            page["text"]
            for page in pages
            if page.get("text")
        )

        extraction_message = (
            f"PDF processed — {len(pages)} pages extracted."
        )

    elif file_name.lower().endswith(".docx"):

        file.seek(0)

        paragraphs = extract_text_from_docx(file)

        extracted_text = "\n".join(
            paragraph["text"]
            for paragraph in paragraphs
            if paragraph.get("text")
        )

        extraction_message = (
            f"DOCX processed — "
            f"{len(paragraphs)} paragraphs extracted."
        )

    elif file_name.lower().endswith(".pptx"):

        file.seek(0)

        slides = extract_text_from_pptx(file)

        extracted_text = "\n".join(
            slide["text"]
            for slide in slides
            if slide.get("text")
        )

        extraction_message = (
            f"PPTX processed — "
            f"{len(slides)} slides extracted."
        )

    else:

        raise ValueError(
            f"Unsupported file type: {file_name}"
        )

    if not extracted_text.strip():
        raise ValueError(
            f"No text could be extracted from {file_name}."
        )

    chunks = chunk_text(extracted_text)

    if not chunks:
        raise ValueError(
            f"No usable text chunks were created for {file_name}."
        )

    embeddings = create_embeddings(chunks)

    file_id = create_file_id(file_bytes)

    store_embeddings(
        chunks,
        embeddings,
        file_name,
        file_id
    )

    return {
        "message": extraction_message,
        "chunks": len(chunks),
        "embeddings": len(embeddings),
    }


def build_context(documents, heading="ACADEMIC SOURCE"):
    """
    Build a formatted academic context from retrieved chunks.
    """

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        context_parts.append(
            f"""
{heading} {index}
========================

{document}
"""
        )

    return "\n".join(context_parts)


def extract_questions_with_progress(pages):
    """
    Extract questions from a question paper with visible progress.

    Small papers are sent as one request. Larger papers are split into
    overlapping page-based chunks so that very large prompts do not have
    to be processed in a single AI request.
    """

    page_texts = [
        str(page.get("text", "")).strip()
        for page in pages
        if page.get("text")
    ]

    page_texts = [
        page_text
        for page_text in page_texts
        if page_text
    ]

    if not page_texts:
        return [], "unknown"

    full_text = "\n\n".join(page_texts)

    # Keep ordinary question papers as a single AI request.
    # This avoids unnecessary extra API calls for small papers.
    max_single_request_chars = 18000

    if len(full_text) <= max_single_request_chars:
        st.info(
            f"📄 Extracted {len(page_texts)} page(s) "
            f"({len(full_text):,} characters)."
        )

        with st.status(
            "🤖 Extracting questions with AI...",
            expanded=True
        ) as status:

            start_time = time.perf_counter()

            questions, provider_used = extract_questions(
                full_text
            )

            elapsed = time.perf_counter() - start_time

            status.update(
                label=(
                    f"✅ Question extraction completed "
                    f"in {elapsed:.1f} seconds."
                ),
                state="complete",
                expanded=False
            )

        return questions, provider_used

    # Large papers are split by pages rather than arbitrary character
    # positions so that a question is less likely to be cut in half.
    max_chunk_chars = 12000
    overlap_pages = 1

    chunks = []
    current_pages = []
    current_length = 0

    for page_text in page_texts:

        additional_length = len(page_text) + (
            2 if current_pages else 0
        )

        if (
            current_pages
            and current_length + additional_length > max_chunk_chars
        ):
            chunks.append(current_pages.copy())

            overlap = current_pages[-overlap_pages:]
            current_pages = overlap.copy()
            current_length = sum(
                len(page) for page in current_pages
            ) + max(0, len(current_pages) - 1) * 2

        current_pages.append(page_text)

        current_length = sum(
            len(page) for page in current_pages
        ) + max(0, len(current_pages) - 1) * 2

    if current_pages:
        chunks.append(current_pages.copy())

    all_questions = []
    providers = []

    st.info(
        f"📄 Extracted {len(page_texts)} page(s) "
        f"({len(full_text):,} characters). "
        f"Large paper detected — processing "
        f"{len(chunks)} AI extraction parts."
    )

    progress_bar = st.progress(0)
    status_text = st.empty()

    extraction_start = time.perf_counter()

    for index, chunk_pages in enumerate(
        chunks,
        start=1
    ):

        chunk_text = "\n\n".join(chunk_pages)

        status_text.info(
            f"🤖 Extracting questions — "
            f"part {index}/{len(chunks)} "
            f"({len(chunk_text):,} characters)"
        )

        questions, provider_used = extract_questions(
            chunk_text
        )

        if questions:
            all_questions.extend(questions)

        providers.append(provider_used)

        progress_bar.progress(
            index / len(chunks)
        )

    elapsed = time.perf_counter() - extraction_start

    status_text.success(
        f"✅ All extraction parts completed in "
        f"{elapsed:.1f} seconds."
    )

    # Remove duplicate questions caused by the overlapping page.
    unique_questions = []
    seen_questions = set()

    for question in all_questions:

        question_text = str(
            question.get("question_text", "")
        ).strip()

        normalized_text = " ".join(
            question_text.lower().split()
        )

        if not normalized_text:
            continue

        if normalized_text in seen_questions:
            continue

        seen_questions.add(normalized_text)
        unique_questions.append(question)

    # Give the final list stable numbering if the model returned
    # duplicated or inconsistent numbering across chunks.
    for index, question in enumerate(
        unique_questions,
        start=1
    ):
        question["question_number"] = str(index)

    provider_names = [
        str(provider)
        for provider in providers
        if provider
    ]

    if not provider_names:
        final_provider = "unknown"
    elif len(set(provider_names)) == 1:
        final_provider = provider_names[0]
    else:
        final_provider = "multiple providers"

    return unique_questions, final_provider


def evaluate_practice_test_batch(practice_questions, academic_context):
    """
    Evaluate all answered practice-test questions in one LLM request.

    This replaces one LLM call per question with a single structured
    evaluation request, which is substantially faster for multi-question
    tests.
    """

    evaluation_items = []

    for index, practice_question in enumerate(
        practice_questions,
        start=1
    ):

        question_number = practice_question.get(
            "question_number",
            index
        )

        question_text = practice_question.get(
            "question",
            practice_question.get(
                "question_text",
                ""
            )
        )

        student_answer = st.session_state.get(
            f"exam_answer_{index}",
            ""
        )

        evaluation_items.append(
            {
                "question_number": question_number,
                "question": question_text,
                "student_answer": student_answer,
            }
        )

    answered_items = [
        item
        for item in evaluation_items
        if str(item["student_answer"]).strip()
    ]

    results_by_number = {}

    # Do not spend an LLM request on unanswered questions.
    for item in evaluation_items:

        if not str(item["student_answer"]).strip():

            results_by_number[str(item["question_number"])] = {
                "result": "Not Attempted",
                "score": 0,
                "feedback": "No answer was provided.",
                "missing_points": [],
                "ideal_answer": "",
            }

    if not answered_items:
        return [
            (
                item,
                results_by_number[
                    str(item["question_number"])
                ],
                "none"
            )
            for item in evaluation_items
        ]

    compact_items = []

    for item in answered_items:

        compact_items.append(
            {
                "question_number": item["question_number"],
                "question": item["question"],
                "student_answer": item["student_answer"],
            }
        )

    prompt = f"""
You are an academic examiner evaluating a student's practice test.

Evaluate ALL answered questions below in ONE response.

Use the academic context as the primary reference.

ACADEMIC CONTEXT:
{academic_context}

QUESTIONS AND STUDENT ANSWERS:
{json.dumps(compact_items, ensure_ascii=False, indent=2)}

For every answered question:
- Score it from 0 to 10.
- Decide whether it is Correct, Partially Correct, or Incorrect.
- Give concise, useful feedback.
- List important missing points.
- Provide a concise ideal answer.
- Do not invent facts that are unsupported by the academic context.

Return ONLY a valid JSON array.
Use exactly this structure:

[
  {{
    "question_number": 1,
    "result": "Correct",
    "score": 8,
    "feedback": "Concise feedback.",
    "missing_points": ["Important missing point"],
    "ideal_answer": "Concise ideal answer."
  }}
]

Return one object for every answered question.
"""

    start_time = time.perf_counter()

    response_text, provider_used = generate_with_fallback(
        prompt,
        academic_context
    )

    elapsed = time.perf_counter() - start_time

    cleaned = response_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1)
        cleaned = cleaned.replace("```", "", 1).strip()

    start_index = cleaned.find("[")
    end_index = cleaned.rfind("]")

    if start_index == -1 or end_index == -1:
        raise ValueError(
            "AI evaluation did not return a valid JSON array."
        )

    evaluation_data = json.loads(
        cleaned[start_index:end_index + 1]
    )

    if not isinstance(evaluation_data, list):
        raise ValueError(
            "AI evaluation returned an invalid result format."
        )

    for item in evaluation_data:

        question_number = str(
            item.get("question_number", "")
        )

        results_by_number[question_number] = {
            "result": str(
                item.get("result", "N/A")
            ),
            "score": item.get("score", 0),
            "feedback": str(
                item.get(
                    "feedback",
                    "No feedback available."
                )
            ),
            "missing_points": item.get(
                "missing_points",
                []
            ),
            "ideal_answer": str(
                item.get(
                    "ideal_answer",
                    ""
                )
            ),
        }

    final_results = []

    for item in evaluation_items:

        question_number = str(
            item["question_number"]
        )

        evaluation = results_by_number.get(
            question_number,
            {
                "result": "Evaluation Unavailable",
                "score": 0,
                "feedback": (
                    "No evaluation was returned "
                    "for this question."
                ),
                "missing_points": [],
                "ideal_answer": "",
            }
        )

        final_results.append(
            (
                item,
                evaluation,
                provider_used
            )
        )

    return final_results


def display_performance_dashboard():
    """
    Display the Week 6/7 performance dashboard.
    """

    history = st.session_state.get(
        "performance_history",
        []
    )

    if not history:

        st.info(
            "No performance data is available yet. "
            "Complete a practice test to start tracking performance."
        )

        return

    summary = get_performance_summary(history)

    overall = summary["overall"]
    topic_performance = summary["topic_performance"]
    weak_areas = summary["weak_areas"]
    strong_areas = summary["strong_areas"]
    recommendations = summary["recommendations"]

    # ----------------------------------------------
    # Overall metrics
    # ----------------------------------------------

    st.subheader("📈 Overall Performance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Tests Attempted",
            overall["tests_attempted"]
        )

    with col2:
        st.metric(
            "Total Score",
            f"{overall['total_score']:g}/{overall['total_marks']:g}"
        )

    with col3:
        st.metric(
            "Overall Percentage",
            f"{overall['percentage']:.1f}%"
        )

    with col4:
        st.metric(
            "Topics Tracked",
            len(topic_performance)
        )

    st.divider()

    # ----------------------------------------------
    # Topic-wise performance
    # ----------------------------------------------

    st.subheader("📚 Topic-Wise Performance")

    if topic_performance:

        topic_rows = []

        for topic, data in topic_performance.items():

            topic_rows.append(
                {
                    "Topic": topic,
                    "Tests": data["tests"],
                    "Score": (
                        f"{data['score']:g}/"
                        f"{data['total_marks']:g}"
                    ),
                    "Percentage": (
                        f"{data['percentage']:.1f}%"
                    ),
                }
            )

        st.table(topic_rows)

        # Native Streamlit chart
        chart_data = {
            topic: data["percentage"]
            for topic, data in topic_performance.items()
        }

        st.caption("Topic performance")

        st.bar_chart(chart_data)

    else:

        st.info(
            "Topic-wise performance is not available yet."
        )

    st.divider()

    # ----------------------------------------------
    # Weak and strong areas
    # ----------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🔎 Weak Areas")

        if weak_areas:

            for area in weak_areas:

                st.warning(
                    f"**{area['topic']}** — "
                    f"{area['percentage']:.1f}%"
                )

        else:

            st.success(
                "No weak areas identified using the current threshold."
            )

    with col2:

        st.subheader("⭐ Strong Areas")

        if strong_areas:

            for area in strong_areas:

                st.success(
                    f"**{area['topic']}** — "
                    f"{area['percentage']:.1f}%"
                )

        else:

            st.info(
                "No strong areas identified yet."
            )

    st.divider()

    # ----------------------------------------------
    # Recommendations
    # ----------------------------------------------

    st.subheader("💡 Personalized Recommendations")

    if recommendations:

        for recommendation in recommendations:

            priority = recommendation["priority"]
            topic = recommendation["topic"]
            percentage = recommendation["percentage"]
            action = recommendation["recommendation"]

            with st.container():

                st.markdown(
                    f"### {topic}"
                )

                st.write(
                    f"Current performance: "
                    f"**{percentage:.1f}%**"
                )

                st.write(
                    f"Priority: **{priority}**"
                )

                st.info(action)

    else:

        st.success(
            "No additional recommendations are required "
            "based on the current performance data."
        )

    st.divider()

    # ----------------------------------------------
    # Performance history
    # ----------------------------------------------

    st.subheader("🕒 Practice Test History")

    history_rows = []

    for index, record in enumerate(
        history,
        start=1
    ):

        history_rows.append(
            {
                "Test": index,
                "Topic": record.get(
                    "topic",
                    "Unknown"
                ),
                "Difficulty": record.get(
                    "difficulty",
                    "Unknown"
                ),
                "Score": (
                    f"{float(record.get('score', 0)):g}/"
                    f"{float(record.get('total_marks', 0)):g}"
                ),
                "Percentage": (
                    f"{float(record.get('percentage', 0)):.1f}%"
                    if "percentage" in record
                    else (
                        f"{(float(record.get('score', 0)) / float(record.get('total_marks', 1)) * 100):.1f}%"
                        if float(record.get("total_marks", 0)) > 0
                        else "0.0%"
                    )
                ),
            }
        )

    st.table(history_rows)


# ==================================================
# HEADER
# ==================================================

st.title("📚 VidyānVaya AI")

st.subheader(
    "A Subject-Agnostic Academic Learning Assistant"
)

st.write(
    "Upload your academic materials and use AI to "
    "learn, solve questions, practice, analyze performance, "
    "and improve."
)


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("📚 VidyānVaya AI")

st.sidebar.caption(
    "Academic Learning Assistant"
)

page = st.sidebar.radio(
    "Navigate",
    [
        "📚 Materials",
        "🧠 Learn",
        "📝 Practice",
        "📊 Performance",
    ],
    key="main_navigation"
)

st.sidebar.divider()

# Database status in sidebar

total_embeddings = get_collection_count()

st.sidebar.metric(
    "Stored Text Chunks",
    total_embeddings
)

documents_available = get_document_names()

st.sidebar.metric(
    "Processed Documents",
    len(documents_available)
)


# ==================================================
# PAGE 1 — MATERIALS
# ==================================================

if page == "📚 Materials":

    st.header("📚 Academic Materials")

    st.write(
        "Upload your notes, textbooks, question papers, "
        "or presentations and add them to the academic knowledge base."
    )

    st.divider()

    uploaded_files = st.file_uploader(
        "Upload academic materials",
        type=[
            "pdf",
            "docx",
            "pptx"
        ],
        accept_multiple_files=True,
        key="academic_file_uploader"
    )

    if uploaded_files:

        save_uploaded_files(uploaded_files)

        st.success(
            f"{len(uploaded_files)} file(s) selected."
        )

        st.subheader("📄 Selected Files")

        for file in uploaded_files:

            st.write(
                f"• {file.name}"
            )

        st.divider()

        if st.button(
            "⚙️ Process / Update Documents",
            type="primary",
            key="process_documents_button"
        ):

            progress_container = st.container()

            with progress_container:

                for file in uploaded_files:

                    st.write(
                        f"📄 Processing: **{file.name}**"
                    )

                    try:

                        result = process_single_document(
                            file.name,
                            file.getvalue()
                        )

                        st.success(
                            f"✅ {file.name} processed successfully."
                        )

                        st.caption(
                            result["message"]
                        )

                        st.caption(
                            f"Created {result['chunks']} "
                            f"chunks and {result['embeddings']} "
                            f"embeddings."
                        )

                    except Exception as e:

                        st.error(
                            f"❌ Could not process "
                            f"{file.name}: {e}"
                        )

    else:

        if st.session_state["uploaded_files_data"]:

            st.info(
                "Previously selected files are stored for this session."
            )

        else:

            st.info(
                "Upload academic materials to get started."
            )

    st.divider()

    # ----------------------------------------------
    # Processed documents
    # ----------------------------------------------

    st.subheader("📚 Processed Academic Materials")

    processed_documents = get_document_names()

    if processed_documents:

        for document in processed_documents:

            st.success(
                f"📖 {document}"
            )

    else:

        st.info(
            "No documents have been processed yet."
        )

    st.divider()

    # ----------------------------------------------
    # Database information
    # ----------------------------------------------

    st.subheader("🗄️ Knowledge Base Status")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Processed Documents",
            len(processed_documents)
        )

    with col2:

        st.metric(
            "Stored Text Chunks",
            get_collection_count()
        )


# ==================================================
# PAGE 2 — LEARN
# ==================================================

elif page == "🧠 Learn":

    st.header("🧠 Learn")

    st.write(
        "Learn from your uploaded academic material "
        "using grounded AI responses."
    )

    learn_mode = st.radio(
        "Choose a learning mode",
        [
            "🔍 Subject Guide",
            "🧠 Question Solver",
        ],
        horizontal=True,
        key="learn_mode"
    )

    st.divider()

    documents = get_document_names()

    if not documents:

        st.warning(
            "No academic material is available. "
            "Go to **📚 Materials** and process a document first."
        )

    else:

        # ==================================================
        # SUBJECT GUIDE
        # ==================================================

        if learn_mode == "🔍 Subject Guide":

            st.subheader("🔍 Ask VidyānVaya AI")

            selected_document = st.selectbox(
                "📚 Select academic material",
                documents,
                key="subject_guide_document"
            )

            st.success(
                f"📖 Currently using: **{selected_document}**"
            )

            query = st.text_area(
                "Enter your question",
                placeholder=(
                    "Example: Explain the OSI model "
                    "with its seven layers."
                ),
                height=100,
                key="subject_guide_query"
            )

            if st.button(
                "🤖 Ask VidyānVaya AI",
                type="primary",
                key="subject_guide_button"
            ):

                if not query.strip():

                    st.warning(
                        "Please enter a question."
                    )

                else:

                    try:

                        with st.spinner(
                            "🔎 Searching the selected document..."
                        ):

                            results = retrieve_relevant_chunks(
                                query=query,
                                source_name=selected_document,
                                n_results=5
                            )

                        documents_found = results.get(
                            "documents",
                            [[]]
                        )[0]

                        distances = results.get(
                            "distances",
                            [[]]
                        )[0]

                        if not documents_found:

                            st.warning(
                                "No relevant information was "
                                "found in this document."
                            )

                        else:

                            st.success(
                                f"🔎 Found "
                                f"{len(documents_found)} "
                                f"relevant text chunks."
                            )

                            context = build_context(
                                documents_found,
                                heading="SOURCE CHUNK"
                            )

                            with st.spinner(
                                "🤖 Generating answer..."
                            ):

                                answer, provider_used = (
                                    generate_with_fallback(
                                        query,
                                        context
                                    )
                                )

                            st.divider()

                            st.subheader("💡 Answer")

                            st.markdown(answer)

                            st.caption(
                                f"🤖 Generated by: "
                                f"{provider_used.capitalize()}"
                            )

                            with st.expander(
                                "📚 View retrieved source information"
                            ):

                                st.caption(
                                    f"Source document: "
                                    f"{selected_document}"
                                )

                                for index, document in enumerate(
                                    documents_found,
                                    start=1
                                ):

                                    st.markdown(
                                        f"### Source {index}"
                                    )

                                    st.write(document)

                                    if index <= len(distances):

                                        st.caption(
                                            f"Distance: "
                                            f"{distances[index - 1]:.4f}"
                                        )

                    except Exception as e:

                        st.error(
                            f"❌ Could not retrieve or "
                            f"generate answer: {e}"
                        )

        # ==================================================
        # QUESTION SOLVER
        # ==================================================

        else:

            st.subheader("🧠 Question Solver")

            questions = st.session_state.get(
                "extracted_questions",
                []
            )

            if not questions:

                st.info(
                    "No extracted questions are available yet. "
                    "Go to **📝 Practice → Question Bank** "
                    "to extract questions from a question paper."
                )

            else:

                selected_solver_document = st.selectbox(
                    "📚 Select study material",
                    documents,
                    key="solver_document_selector"
                )

                question_options = [
                    (
                        question.get(
                            "question_number",
                            ""
                        ),
                        question.get(
                            "question_text",
                            ""
                        )
                    )
                    for question in questions
                ]

                selected_question = st.selectbox(
                    "❓ Select a question to solve",
                    question_options,
                    format_func=lambda q: (
                        f"{q[0]} — "
                        f"{q[1][:120]}"
                        + (
                            "..."
                            if len(q[1]) > 120
                            else ""
                        )
                    ),
                    key="solver_question_selector"
                )

                question_number = selected_question[0]
                question_text = selected_question[1]

                st.markdown(
                    "### ❓ Selected Question"
                )

                st.info(
                    f"**{question_number}**\n\n"
                    f"{question_text}"
                )

                if st.button(
                    "🧠 Solve Question",
                    type="primary",
                    key="solve_question_button"
                ):

                    try:

                        with st.spinner(
                            "🔎 Searching your academic material..."
                        ):

                            results = retrieve_relevant_chunks(
                                query=question_text,
                                source_name=selected_solver_document,
                                n_results=5
                            )

                        documents_found = results.get(
                            "documents",
                            [[]]
                        )[0]

                        distances = results.get(
                            "distances",
                            [[]]
                        )[0]

                        if not documents_found:

                            st.warning(
                                "No relevant information was found "
                                "in the selected academic material."
                            )

                        else:

                            st.success(
                                f"🔎 Found "
                                f"{len(documents_found)} "
                                f"relevant academic chunks."
                            )

                            academic_context = build_context(
                                documents_found,
                                heading="ACADEMIC SOURCE"
                            )

                            solver_context = f"""
You are VidyānVaya AI's Question Solver.

Answer the student's examination question using ONLY the
retrieved academic material below as the primary source.

Requirements:
- Answer every sub-part.
- Use clear exam-oriented headings and bullet points.
- Include definitions, explanations, formulas, examples, or
  calculation steps when supported by the material.
- Keep the answer complete but concise.
- Do not introduce unrelated information.
- Do not invent unsupported facts or formulas.
- If the material is insufficient, say:
  "I could not find enough information in the uploaded materials
  to answer this question."

RETRIEVED ACADEMIC MATERIAL
===========================
{academic_context}

STUDENT QUESTION
================
{question_text}

Now provide the final exam-oriented answer.
"""

                            generation_start = time.perf_counter()

                            with st.spinner(
                                "🤖 Generating exam-ready solution..."
                            ):

                                answer, provider_used = (
                                    generate_with_fallback(
                                        question_text,
                                        solver_context
                                    )
                                )

                            generation_elapsed = (
                                time.perf_counter() - generation_start
                            )

                            st.success(
                                f"✅ Solution generated in "
                                f"{generation_elapsed:.1f} seconds "
                                f"using {provider_used.capitalize()}."
                            )

                            st.divider()

                            st.header("💡 Solution")

                            st.markdown(answer)

                            st.caption(
                                f"🤖 Generated by: "
                                f"{provider_used.capitalize()}"
                            )

                            with st.expander(
                                "📚 View academic sources used"
                            ):

                                st.caption(
                                    f"Study material: "
                                    f"{selected_solver_document}"
                                )

                                for index, document in enumerate(
                                    documents_found,
                                    start=1
                                ):

                                    st.markdown(
                                        f"### Source {index}"
                                    )

                                    st.write(document)

                                    if index <= len(distances):

                                        st.caption(
                                            f"Distance: "
                                            f"{distances[index - 1]:.4f}"
                                        )

                    except Exception as e:

                        st.error(
                            f"❌ Could not solve the question: {e}"
                        )


# ==================================================
# PAGE 3 — PRACTICE
# ==================================================

elif page == "📝 Practice":

    st.header("📝 Practice")

    st.write(
        "Practice with previous-year questions and "
        "AI-generated examination tests."
    )

    practice_mode = st.radio(
        "Choose a practice mode",
        [
            "📝 Question Bank",
            "🎯 Exam Preparation",
        ],
        horizontal=True,
        key="practice_mode"
    )

    st.divider()

    # ==================================================
    # QUESTION BANK
    # ==================================================

    if practice_mode == "📝 Question Bank":

        st.subheader("📝 Question Bank")

        st.write(
            "Upload or select a question paper. "
            "VidyānVaya AI first extracts the PDF text and then "
            "identifies the individual questions."
        )

        pdf_names = get_uploaded_pdf_names()

        if not pdf_names:

            st.warning(
                "No PDF question paper is available in the "
                "current session. Go to **📚 Materials** "
                "and upload a PDF question paper."
            )

        else:

            selected_question_paper = st.selectbox(
                "Select a question paper",
                pdf_names,
                key="question_paper_selector"
            )

            if st.button(
                "📝 Extract Questions",
                type="primary",
                key="extract_questions_button"
            ):

                try:

                    question_paper_file = create_file_object(
                        selected_question_paper
                    )

                    if question_paper_file is None:

                        st.error(
                            "Could not load the selected question paper."
                        )

                    else:

                        with st.status(
                            "🔎 Reading question paper...",
                            expanded=True
                        ) as pdf_status:

                            pdf_start = time.perf_counter()

                            st.write(
                                "📄 Extracting text from the PDF..."
                            )

                            pages = extract_text_from_pdf(
                                question_paper_file
                            )

                            page_count = len(pages)

                            question_paper_text = "\n".join(
                                page["text"]
                                for page in pages
                                if page.get("text")
                            )

                            pdf_elapsed = (
                                time.perf_counter() - pdf_start
                            )

                            if not question_paper_text.strip():

                                pdf_status.update(
                                    label=(
                                        "❌ No text could be extracted "
                                        "from the question paper."
                                    ),
                                    state="error",
                                    expanded=True
                                )

                                st.warning(
                                    "No text could be extracted "
                                    "from the selected question paper."
                                )

                            else:

                                pdf_status.update(
                                    label=(
                                        f"✅ PDF text extracted — "
                                        f"{page_count} page(s) in "
                                        f"{pdf_elapsed:.1f} seconds."
                                    ),
                                    state="complete",
                                    expanded=False
                                )

                                questions, provider_used = (
                                    extract_questions_with_progress(
                                        pages
                                    )
                                )

                                st.session_state[
                                    "extracted_questions"
                                ] = questions

                                st.session_state[
                                    "question_bank_provider"
                                ] = provider_used

                                st.session_state[
                                    "question_bank_source"
                                ] = selected_question_paper

                                if questions:

                                    st.success(
                                        f"✅ Extracted "
                                        f"{len(questions)} questions "
                                        f"from "
                                        f"{selected_question_paper}"
                                    )

                                else:

                                    st.warning(
                                        "No questions could be identified "
                                        "in the selected question paper."
                                    )

                except Exception as e:

                    st.error(
                        f"❌ Could not extract questions: {e}"
                    )

        # ----------------------------------------------
        # Display extracted questions
        # ----------------------------------------------

        questions = st.session_state.get(
            "extracted_questions",
            []
        )

        if questions:

            provider_used = st.session_state.get(
                "question_bank_provider",
                "unknown"
            )

            source_name = st.session_state.get(
                "question_bank_source",
                "Unknown"
            )

            st.divider()

            st.success(
                f"✅ {len(questions)} questions available "
                f"from {source_name}"
            )

            st.caption(
                f"🤖 Generated by: "
                f"{provider_used.capitalize()}"
            )

            st.subheader("📋 Extracted Questions")

            for question in questions:

                question_number = question.get(
                    "question_number",
                    ""
                )

                question_text = question.get(
                    "question_text",
                    ""
                )

                with st.container():

                    st.markdown(
                        f"### {question_number}"
                    )

                    st.write(
                        question_text
                    )

                    st.divider()

        else:

            st.info(
                "No questions have been extracted yet."
            )

    # ==================================================
    # EXAM PREPARATION
    # ==================================================

    else:

        st.subheader("🎯 Exam Preparation")

        st.write(
            "Generate AI-powered practice questions from "
            "your uploaded academic material and evaluate your answers."
        )

        exam_documents = get_document_names()

        if not exam_documents:

            st.info(
                "Upload and process academic material first "
                "to start exam preparation."
            )

        else:

            st.subheader("📚 Practice Test Setup")

            selected_exam_document = st.selectbox(
                "Select study material",
                exam_documents,
                key="exam_prep_document_selector"
            )

            col1, col2 = st.columns(2)

            with col1:

                exam_topic = st.text_input(
                    "Topic",
                    placeholder=(
                        "Example: Computer Organization"
                    ),
                    key="exam_prep_topic_input"
                )

            with col2:

                exam_difficulty = st.selectbox(
                    "Difficulty",
                    [
                        "Easy",
                        "Medium",
                        "Hard"
                    ],
                    index=1,
                    key="exam_prep_difficulty_selector"
                )

            exam_question_count = st.slider(
                "Number of questions",
                min_value=1,
                max_value=10,
                value=3,
                key="exam_prep_question_count"
            )

            if st.button(
                "🎯 Generate Practice Test",
                type="primary",
                key="generate_practice_test_button"
            ):

                if not exam_topic.strip():

                    st.warning(
                        "Please enter a topic before generating "
                        "the practice test."
                    )

                else:

                    try:

                        with st.spinner(
                            "🔎 Searching your academic material..."
                        ):

                            exam_results = (
                                retrieve_relevant_chunks(
                                    query=exam_topic,
                                    source_name=selected_exam_document,
                                    n_results=8
                                )
                            )

                        exam_documents_found = (
                            exam_results.get(
                                "documents",
                                [[]]
                            )[0]
                        )

                        if not exam_documents_found:

                            st.warning(
                                "No relevant academic material was found "
                                "for this topic."
                            )

                        else:

                            st.success(
                                f"🔎 Found "
                                f"{len(exam_documents_found)} "
                                f"relevant academic chunks."
                            )

                            exam_context = build_context(
                                exam_documents_found,
                                heading="ACADEMIC SOURCE"
                            )

                            with st.spinner(
                                "🤖 Generating practice questions..."
                            ):

                                (
                                    practice_questions,
                                    provider_used
                                ) = generate_practice_test(
                                    academic_context=exam_context,
                                    number_of_questions=(
                                        exam_question_count
                                    ),
                                    difficulty=exam_difficulty,
                                    topic=exam_topic
                                )

                            if not practice_questions:

                                st.warning(
                                    "The AI could not generate practice "
                                    "questions from the selected material."
                                )

                            else:

                                st.session_state[
                                    "exam_prep_questions"
                                ] = practice_questions

                                st.session_state[
                                    "exam_prep_provider"
                                ] = provider_used

                                st.session_state[
                                    "exam_prep_document"
                                ] = selected_exam_document

                                st.session_state[
                                    "exam_prep_topic"
                                ] = exam_topic

                                st.session_state[
                                    "exam_prep_difficulty"
                                ] = exam_difficulty

                                st.session_state[
                                    "exam_prep_context"
                                ] = exam_context

                                st.session_state[
                                    "exam_prep_source_chunks"
                                ] = exam_documents_found

                                st.session_state.pop(
                                    "exam_prep_results",
                                    None
                                )

                                st.session_state[
                                    "exam_prep_total_score"
                                ] = 0

                                st.success(
                                    f"✅ Generated "
                                    f"{len(practice_questions)} "
                                    f"practice questions."
                                )

                                st.caption(
                                    f"🤖 Generated by: "
                                    f"{provider_used.capitalize()}"
                                )

                    except Exception as e:

                        st.error(
                            f"❌ Could not generate practice test: {e}"
                        )

            # ------------------------------------------
            # Display generated practice test
            # ------------------------------------------

            practice_questions = st.session_state.get(
                "exam_prep_questions",
                []
            )

            if practice_questions:

                st.divider()

                st.subheader("📋 Practice Test")

                st.caption(
                    f"Study material: "
                    f"{st.session_state.get('exam_prep_document', 'Unknown')}"
                )

                st.caption(
                    f"Topic: "
                    f"{st.session_state.get('exam_prep_topic', 'Unknown')}"
                    f" | Difficulty: "
                    f"{st.session_state.get('exam_prep_difficulty', 'Medium')}"
                )

                for index, practice_question in enumerate(
                    practice_questions,
                    start=1
                ):

                    question_number = (
                        practice_question.get(
                            "question_number",
                            index
                        )
                    )

                    question_text = (
                        practice_question.get(
                            "question",
                            practice_question.get(
                                "question_text",
                                ""
                            )
                        )
                    )

                    question_difficulty = (
                        practice_question.get(
                            "difficulty",
                            st.session_state.get(
                                "exam_prep_difficulty",
                                "Medium"
                            )
                        )
                    )

                    st.markdown(
                        f"### Question {question_number}"
                    )

                    st.write(question_text)

                    st.caption(
                        f"Difficulty: {question_difficulty}"
                    )

                    st.text_area(
                        "Your answer",
                        key=f"exam_answer_{index}",
                        height=160
                    )

                    st.divider()

                if st.button(
                    "✅ Submit Practice Test",
                    type="primary",
                    key="submit_exam_prep_button"
                ):

                    evaluation_results = []
                    total_score = 0

                    with st.status(
                        "🤖 Evaluating your practice test...",
                        expanded=True
                    ) as evaluation_status:

                        evaluation_start = time.perf_counter()

                        st.write(
                            "📚 Preparing all answered questions "
                            "for one AI evaluation request..."
                        )

                        batch_results = (
                            evaluate_practice_test_batch(
                                practice_questions,
                                st.session_state[
                                    "exam_prep_context"
                                ]
                            )
                        )

                        for (
                            item,
                            evaluation,
                            evaluation_provider
                        ) in batch_results:

                            score = evaluation.get(
                                "score",
                                0
                            )

                            try:
                                score = float(score)
                            except (
                                TypeError,
                                ValueError
                            ):
                                score = 0

                            score = max(
                                0,
                                min(10, score)
                            )

                            total_score += score

                            evaluation_results.append(
                                {
                                    "question_number":
                                        item[
                                            "question_number"
                                        ],
                                    "question":
                                        item[
                                            "question"
                                        ],
                                    "student_answer":
                                        item[
                                            "student_answer"
                                        ],
                                    "evaluation":
                                        evaluation,
                                    "provider":
                                        evaluation_provider
                                }
                            )

                        evaluation_elapsed = (
                            time.perf_counter()
                            - evaluation_start
                        )

                        evaluation_status.update(
                            label=(
                                f"✅ Practice test evaluated in "
                                f"{evaluation_elapsed:.1f} seconds."
                            ),
                            state="complete",
                            expanded=False
                        )

                    st.session_state[
                        "exam_prep_results"
                    ] = evaluation_results

                    st.session_state[
                        "exam_prep_total_score"
                    ] = total_score

                    # ------------------------------------------
                    # Week 6 performance tracking
                    # ------------------------------------------

                    practice_record = {
                        "topic": (
                            st.session_state.get(
                                "exam_prep_topic",
                                "Unknown"
                            )
                        ),
                        "difficulty": (
                            st.session_state.get(
                                "exam_prep_difficulty",
                                "Medium"
                            )
                        ),
                        "score": total_score,
                        "total_marks": (
                            len(evaluation_results) * 10
                        ),
                        "questions_attempted": (
                            len(evaluation_results)
                        ),
                    }

                    st.session_state[
                        "performance_history"
                    ].append(
                        practice_record
                    )

                    st.success(
                        "✅ Practice test evaluated successfully."
                    )

                # ------------------------------------------
                # Display evaluation results
                # ------------------------------------------

                evaluation_results = st.session_state.get(
                    "exam_prep_results",
                    []
                )

                if evaluation_results:

                    st.divider()

                    st.subheader(
                        "📊 Your Performance"
                    )

                    total_score = st.session_state.get(
                        "exam_prep_total_score",
                        0
                    )

                    max_score = (
                        len(evaluation_results) * 10
                    )

                    percentage = (
                        (total_score / max_score) * 100
                        if max_score > 0
                        else 0
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Score",
                            f"{total_score:g}/{max_score}"
                        )

                    with col2:

                        st.metric(
                            "Percentage",
                            f"{percentage:.1f}%"
                        )

                    with col3:

                        st.metric(
                            "Questions",
                            len(evaluation_results)
                        )

                    for result in evaluation_results:

                        evaluation = result[
                            "evaluation"
                        ]

                        st.markdown(
                            f"### Question "
                            f"{result['question_number']}"
                        )

                        st.write(
                            result["question"]
                        )

                        st.markdown(
                            "**Your Answer:**"
                        )

                        if result[
                            "student_answer"
                        ].strip():

                            st.write(
                                result["student_answer"]
                            )

                        else:

                            st.write(
                                "*Not attempted*"
                            )

                        st.markdown(
                            f"**Result:** "
                            f"{evaluation.get('result', 'N/A')}"
                        )

                        st.markdown(
                            f"**Score:** "
                            f"{evaluation.get('score', 0)}/10"
                        )

                        st.markdown(
                            "**Feedback:**"
                        )

                        st.write(
                            evaluation.get(
                                "feedback",
                                "No feedback available."
                            )
                        )

                        missing_points = (
                            evaluation.get(
                                "missing_points",
                                []
                            )
                        )

                        if missing_points:

                            st.markdown(
                                "**Points to Improve:**"
                            )

                            for point in missing_points:

                                st.write(
                                    f"- {point}"
                                )

                        ideal_answer = (
                            evaluation.get(
                                "ideal_answer",
                                ""
                            )
                        )

                        if ideal_answer:

                            with st.expander(
                                "💡 View Ideal Answer"
                            ):

                                st.write(
                                    ideal_answer
                                )

                        st.divider()


# ==================================================
# PAGE 4 — PERFORMANCE
# ==================================================

elif page == "📊 Performance":

    st.header("📊 Performance Dashboard")

    st.write(
        "Analyze your practice-test performance, "
        "identify weak and strong areas, and view "
        "personalized study recommendations."
    )

    st.divider()

    display_performance_dashboard()


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "VidyānVaya AI — AI-powered academic learning assistant"
)

import sys
from pathlib import Path

import streamlit as st


# --------------------------------------------------
# Project path
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# --------------------------------------------------
# Document processing
# --------------------------------------------------

from document_processing.pdf_processor import (
    extract_text_from_pdf
)

from document_processing.docx_processor import (
    extract_text_from_docx
)

from document_processing.pptx_processor import (
    extract_text_from_pptx
)


# --------------------------------------------------
# RAG
# --------------------------------------------------

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


# --------------------------------------------------
# LLM
# --------------------------------------------------

from services.ai_provider import (
    generate_with_fallback
)

from services.question_bank_service import (
    extract_questions
)


# --------------------------------------------------
# Streamlit configuration
# --------------------------------------------------

st.set_page_config(
    page_title="VidyānVaya AI",
    page_icon="📚",
    layout="wide"
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("📚 VidyānVaya AI")

st.subheader(
    "A Subject-Agnostic Academic Learning Assistant"
)

st.write(
    "Upload your academic materials and use AI to "
    "learn, solve questions, practice, and improve."
)

st.divider()


# ==================================================
# DOCUMENT UPLOAD
# ==================================================

st.header("📂 Upload Academic Materials")

uploaded_files = st.file_uploader(
    "Upload your notes, textbooks, "
    "question papers, or presentations",
    type=[
        "pdf",
        "docx",
        "pptx"
    ],
    accept_multiple_files=True
)


# --------------------------------------------------
# Process button
# --------------------------------------------------

if uploaded_files:

    st.success(
        f"{len(uploaded_files)} file(s) selected."
    )

    process_files = st.button(
        "⚙️ Process / Update Documents",
        type="primary"
    )

    if process_files:

        for file in uploaded_files:

            st.write(
                f"📄 Processing: **{file.name}**"
            )

            extracted_text = ""

            try:

                # ----------------------------------
                # PDF
                # ----------------------------------

                if file.name.lower().endswith(".pdf"):

                    file.seek(0)

                    pages = extract_text_from_pdf(
                        file
                    )

                    extracted_text = "\n".join(
                        page["text"]
                        for page in pages
                        if page.get("text")
                    )

                    st.success(
                        f"PDF processed — "
                        f"{len(pages)} pages extracted."
                    )


                # ----------------------------------
                # DOCX
                # ----------------------------------

                elif file.name.lower().endswith(".docx"):

                    file.seek(0)

                    paragraphs = extract_text_from_docx(
                        file
                    )

                    extracted_text = "\n".join(
                        paragraph["text"]
                        for paragraph in paragraphs
                        if paragraph.get("text")
                    )

                    st.success(
                        f"DOCX processed — "
                        f"{len(paragraphs)} paragraphs extracted."
                    )


                # ----------------------------------
                # PPTX
                # ----------------------------------

                elif file.name.lower().endswith(".pptx"):

                    file.seek(0)

                    slides = extract_text_from_pptx(
                        file
                    )

                    extracted_text = "\n".join(
                        slide["text"]
                        for slide in slides
                        if slide.get("text")
                    )

                    st.success(
                        f"PPTX processed — "
                        f"{len(slides)} slides extracted."
                    )


                # ----------------------------------
                # Check extraction
                # ----------------------------------

                if not extracted_text.strip():

                    st.warning(
                        f"No text could be extracted "
                        f"from {file.name}."
                    )

                    continue


                # ----------------------------------
                # Create chunks
                # ----------------------------------

                chunks = chunk_text(
                    extracted_text
                )

                st.info(
                    f"🧩 Created {len(chunks)} "
                    f"text chunks."
                )


                # ----------------------------------
                # Create embeddings
                # ----------------------------------

                with st.spinner(
                    "🧠 Creating embeddings..."
                ):

                    embeddings = create_embeddings(
                        chunks
                    )

                st.success(
                    f"Created {len(embeddings)} embeddings."
                )


                # ----------------------------------
                # Create stable file ID
                # ----------------------------------

                file_bytes = file.getvalue()

                file_id = create_file_id(
                    file_bytes
                )


                # ----------------------------------
                # Store embeddings
                # ----------------------------------

                with st.spinner(
                    "💾 Storing document in vector database..."
                ):

                    store_embeddings(
                        chunks,
                        embeddings,
                        file.name,
                        file_id
                    )

                st.success(
                    f"✅ {file.name} stored successfully."
                )


            except Exception as e:

                st.error(
                    f"❌ Could not process "
                    f"{file.name}: {e}"
                )


# ==================================================
# QUESTION BANK
# ==================================================

st.divider()

st.header("📝 Question Bank")

st.write(
    "Upload a question paper and let VidyānVaya AI "
    "extract the individual questions automatically."
)


if uploaded_files:

    question_papers = [
        file
        for file in uploaded_files
        if file.name.lower().endswith(".pdf")
    ]


    if question_papers:

        selected_question_paper = st.selectbox(
            "Select a question paper",
            question_papers,
            format_func=lambda file: file.name,
            key="question_paper_selector"
        )


        extract_button = st.button(
            "📝 Extract Questions",
            type="primary",
            key="extract_questions_button"
        )


        if extract_button:

            try:

                selected_question_paper.seek(0)

                with st.spinner(
                    "🔎 Reading question paper and extracting questions..."
                ):

                    # --------------------------------------------
                    # Extract text
                    # --------------------------------------------

                    pages = extract_text_from_pdf(
                        selected_question_paper
                    )


                    question_paper_text = "\n".join(
                        page["text"]
                        for page in pages
                        if page.get("text")
                    )


                    if not question_paper_text.strip():

                        st.warning(
                            "No text could be extracted "
                            "from the selected question paper."
                        )

                    else:

                        # ----------------------------------------
                        # AI question extraction
                        # ----------------------------------------

                        questions, provider_used = (
                            extract_questions(
                                question_paper_text
                            )
                        )


                        # ----------------------------------------
                        # Store results
                        # ----------------------------------------

                        st.session_state[
                            "extracted_questions"
                        ] = questions

                        st.session_state[
                            "question_bank_provider"
                        ] = provider_used

                        st.session_state[
                            "question_bank_source"
                        ] = selected_question_paper.name


            except Exception as e:

                st.error(
                    f"❌ Could not extract questions: {e}"
                )


# --------------------------------------------------
# Display extracted questions
# --------------------------------------------------

if "extracted_questions" in st.session_state:

    questions = st.session_state[
        "extracted_questions"
    ]


    provider_used = st.session_state.get(
        "question_bank_provider",
        "unknown"
    )


    source_name = st.session_state.get(
        "question_bank_source",
        "Unknown"
    )


    if questions:

        st.success(
            f"✅ Extracted {len(questions)} questions "
            f"from {source_name}"
        )


        st.caption(
            f"🤖 Generated by: "
            f"{provider_used.capitalize()}"
        )


        st.divider()

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

        st.warning(
            "No questions could be identified "
            "in the selected question paper."
        )


# ==================================================
# QUESTION SOLVER
# ==================================================

st.divider()

st.header("🧠 Question Solver")

st.write(
    "Select an extracted question and solve it using "
    "your uploaded academic material."
)


if "extracted_questions" in st.session_state:

    questions = st.session_state[
        "extracted_questions"
    ]


    if questions:

        # ------------------------------------------
        # Select study material
        # ------------------------------------------

        solver_documents = get_document_names()


        if not solver_documents:

            st.warning(
                "No academic material is available. "
                "Upload and process notes, textbooks, "
                "or other study material first."
            )


        else:

            selected_solver_document = st.selectbox(
                "📚 Select study material",
                solver_documents,
                key="solver_document_selector"
            )


            # ------------------------------------------
            # Select question
            # ------------------------------------------

            question_options = [
                (
                    question["question_number"],
                    question["question_text"]
                )
                for question in questions
            ]


            selected_question = st.selectbox(
                "❓ Select a question to solve",
                question_options,
                format_func=lambda q: (
                    f"{q[0]} — {q[1][:120]}"
                    + ("..." if len(q[1]) > 120 else "")
                ),
                key="solver_question_selector"
            )


            question_number = selected_question[0]

            question_text = selected_question[1]


            # ------------------------------------------
            # Display selected question
            # ------------------------------------------

            st.markdown(
                "### ❓ Selected Question"
            )


            st.info(
                f"**{question_number}**\n\n"
                f"{question_text}"
            )


            # ------------------------------------------
            # Solve button
            # ------------------------------------------

            solve_button = st.button(
                "🧠 Solve Question",
                type="primary",
                key="solve_question_button"
            )


            if solve_button:

                try:

                    # --------------------------------------
                    # Retrieve academic material
                    # --------------------------------------

                    with st.spinner(
                        "🔎 Searching your academic material..."
                    ):

                        results = retrieve_relevant_chunks(
                            query=question_text,
                            source_name=selected_solver_document,
                            n_results=8
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


                        # ----------------------------------
                        # Build retrieved context
                        # ----------------------------------

                        context_parts = []


                        for index, document in enumerate(
                            documents_found,
                            start=1
                        ):

                            context_parts.append(
                                f"""
ACADEMIC SOURCE {index}
======================

{document}
"""
                            )


                        academic_context = "\n".join(
                            context_parts
                        )


                        # ----------------------------------
                        # Build solver instructions
                        # ----------------------------------

                        solver_context = f"""
You are VidyānVaya AI's Question Solver.

Your task is to answer the student's examination
question using the retrieved academic material below.

The retrieved academic material is the PRIMARY SOURCE.

IMPORTANT RULES:

1. Answer the student's question directly.

2. Use the retrieved academic material for:
   - definitions
   - concepts
   - explanations
   - formulas
   - methods
   - examples

3. Give an exam-oriented answer that a student
   can study and write in an examination.

4. If the question contains multiple sub-parts,
   answer every sub-part separately.

5. For each theoretical answer, use a clear structure:
   Definition / Introduction
   → Explanation
   → Important points
   → Example or diagram description when appropriate
   → Conclusion

6. For numerical questions, show:
   Formula
   → Substitution
   → Calculation
   → Final Answer

7. You may derive an answer using concepts or
   formulas present in the retrieved material even
   if the exact question is not written there.

8. Do not introduce unrelated external information.

9. Do not invent facts, formulas, or methods that
   are unsupported by the academic material.

10. If the retrieved material genuinely does not
    contain enough information to answer reliably,
    say exactly:

"I could not find enough information in the
uploaded materials to answer this question."

11. Do not reveal internal reasoning or hidden
    chain-of-thought.

12. Give the final answer clearly and completely.

==================================================
RETRIEVED ACADEMIC MATERIAL
==================================================

{academic_context}

==================================================
STUDENT QUESTION
==================================================

{question_text}

==================================================

Now provide the complete exam-oriented answer.
"""


                        # ----------------------------------
                        # Generate solution
                        # ----------------------------------

                        with st.spinner(
                            "🤖 Generating exam-ready solution..."
                        ):

                            answer, provider_used = (
                                generate_with_fallback(
                                    question_text,
                                    solver_context
                                )
                            )


                        # ----------------------------------
                        # Display solution
                        # ----------------------------------

                        st.divider()

                        st.header(
                            "💡 Solution"
                        )


                        st.markdown(
                            answer
                        )


                        st.caption(
                            f"🤖 Generated by: "
                            f"{provider_used.capitalize()}"
                        )


                        # ----------------------------------
                        # Display sources
                        # ----------------------------------

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


                                st.write(
                                    document
                                )


                                if index < len(distances):

                                    st.caption(
                                        f"Distance: "
                                        f"{distances[index]:.4f}"
                                    )


                except Exception as e:

                    st.error(
                        f"❌ Could not solve the question: {e}"
                    )


# --------------------------------------------------
# Database status
# --------------------------------------------------

st.divider()

total_embeddings = get_collection_count()

st.info(
    f"📊 Total text chunks stored: "
    f"{total_embeddings}"
)


# ==================================================
# DOCUMENT SELECTION
# ==================================================

st.divider()

st.header("📚 Select Your Academic Material")

documents = get_document_names()


if not documents:

    st.info(
        "Upload and process an academic document "
        "to start asking questions."
    )


else:

    selected_document = st.selectbox(
        "Which document do you want to ask about?",
        documents
    )


    st.success(
        f"📖 Currently using: "
        f"**{selected_document}**"
    )


    # ==================================================
    # QUESTION ANSWERING
    # ==================================================

    st.header("🔍 Ask VidyānVaya AI")

    st.write(
        "Ask a question based only on the "
        "selected academic material."
    )


    query = st.text_input(
        "Enter your question"
    )


    if query:

        try:

            # ------------------------------------------
            # Retrieval
            # ------------------------------------------

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


                # --------------------------------------
                # Build context
                # --------------------------------------

                context_parts = []


                for index, document in enumerate(
                    documents_found,
                    start=1
                ):

                    context_parts.append(
                        f"""
SOURCE CHUNK {index}
-------------------
{document}
"""
                    )


                context = "\n".join(
                    context_parts
                )


                # --------------------------------------
                # Generate answer
                # --------------------------------------

                with st.spinner(
                    "🤖 Generating answer..."
                ):

                    answer, provider_used = (
                        generate_with_fallback(
                            query,
                            context
                        )
                    )


                # --------------------------------------
                # Display answer
                # --------------------------------------

                st.divider()

                st.header(
                    "💡 Answer"
                )


                st.markdown(
                    answer
                )


                st.caption(
                    f"🤖 Generated by: "
                    f"{provider_used.capitalize()}"
                )


                # --------------------------------------
                # Source information
                # --------------------------------------

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


                        st.write(
                            document
                        )


                        if index < len(distances):

                            st.caption(
                                f"Distance: "
                                f"{distances[index]:.4f}"
                            )


        except Exception as e:

            st.error(
                f"❌ Could not retrieve or "
                f"generate answer: {e}"
            )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "VidyānVaya AI — AI-powered academic learning assistant"
)
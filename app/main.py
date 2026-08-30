import sys
from pathlib import Path

import streamlit as st


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="VidyānVaya AI",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# IMPORT PROJECT MODULES
# =========================================================

try:

    from document_processing.pdf_processor import (
        extract_text_from_pdf
    )

    from document_processing.docx_processor import (
        extract_text_from_docx
    )

    from document_processing.pptx_processor import (
        extract_text_from_pptx
    )

    from rag.chunking import chunk_text

    from rag.embeddings import create_embeddings

    from rag.vector_store import (
        store_embeddings,
        get_collection_count
    )

    from rag.retrieval import (
        retrieve_relevant_chunks
    )

    from services.llm_service import (
        generate_answer
    )

except ModuleNotFoundError as e:

    st.error(
        f"Missing Python package/module: {e}"
    )

    st.info(
        "Please install the project dependencies "
        "and restart Streamlit."
    )

    st.stop()


# =========================================================
# HEADER
# =========================================================

st.title("📚 VidyānVaya AI")

st.subheader(
    "A Subject-Agnostic Academic Learning Assistant"
)

st.write(
    "Upload your academic materials and use AI to "
    "learn, solve questions, practice, and improve."
)


# =========================================================
# DOCUMENT UPLOAD
# =========================================================

st.divider()

st.header("📂 Upload Academic Materials")

uploaded_files = st.file_uploader(
    "Upload your notes, textbooks, question papers, or presentations",
    type=["pdf", "docx", "pptx"],
    accept_multiple_files=True
)


if uploaded_files:

    st.success(
        f"{len(uploaded_files)} file(s) uploaded."
    )

    for file in uploaded_files:

        st.markdown(
            f"### 📄 {file.name}"
        )

        extracted_text = ""


        # =================================================
        # PDF
        # =================================================

        if file.name.lower().endswith(".pdf"):

            try:

                pages = extract_text_from_pdf(file)

                extracted_text = "\n".join(
                    page["text"]
                    for page in pages
                    if page.get("text")
                )

                st.success(
                    f"PDF processed successfully — "
                    f"{len(pages)} pages, "
                    f"{len(extracted_text):,} characters extracted."
                )

                with st.expander(
                    "Preview extracted text"
                ):

                    for page in pages[:3]:

                        st.markdown(
                            f"**Page {page['page_number']}**"
                        )

                        st.write(
                            page["text"][:1500]
                        )

            except Exception as e:

                st.error(
                    f"Could not process PDF: {e}"
                )

                continue


        # =================================================
        # DOCX
        # =================================================

        elif file.name.lower().endswith(".docx"):

            try:

                paragraphs = extract_text_from_docx(
                    file
                )

                extracted_text = "\n".join(
                    paragraph["text"]
                    for paragraph in paragraphs
                    if paragraph.get("text")
                )

                st.success(
                    f"DOCX processed successfully — "
                    f"{len(paragraphs)} paragraphs, "
                    f"{len(extracted_text):,} characters extracted."
                )

                with st.expander(
                    "Preview extracted text"
                ):

                    for paragraph in paragraphs[:20]:

                        st.write(
                            paragraph["text"]
                        )

            except Exception as e:

                st.error(
                    f"Could not process DOCX: {e}"
                )

                continue


        # =================================================
        # PPTX
        # =================================================

        elif file.name.lower().endswith(".pptx"):

            try:

                slides = extract_text_from_pptx(
                    file
                )

                extracted_text = "\n".join(
                    slide["text"]
                    for slide in slides
                    if slide.get("text")
                )

                st.success(
                    f"PPTX processed successfully — "
                    f"{len(slides)} slides, "
                    f"{len(extracted_text):,} characters extracted."
                )

                with st.expander(
                    "Preview extracted text"
                ):

                    for slide in slides[:5]:

                        st.markdown(
                            f"**Slide {slide['slide_number']}**"
                        )

                        st.write(
                            slide["text"][:1500]
                        )

            except Exception as e:

                st.error(
                    f"Could not process PPTX: {e}"
                )

                continue


        # =================================================
        # RAG PIPELINE
        # =================================================

        if extracted_text.strip():

            try:

                # -----------------------------------------
                # 1. CHUNKING
                # -----------------------------------------

                with st.spinner(
                    "🧩 Splitting document into chunks..."
                ):

                    chunks = chunk_text(
                        extracted_text
                    )

                st.info(
                    f"🧩 {len(chunks)} text chunks created."
                )


                # -----------------------------------------
                # CHUNK PREVIEW
                # -----------------------------------------

                with st.expander(
                    "Preview text chunks"
                ):

                    for index, chunk in enumerate(
                        chunks[:5],
                        start=1
                    ):

                        st.markdown(
                            f"**Chunk {index}**"
                        )

                        st.write(chunk)


                # -----------------------------------------
                # 2. EMBEDDINGS
                # -----------------------------------------

                with st.spinner(
                    "🧠 Creating embeddings..."
                ):

                    embeddings = create_embeddings(
                        chunks
                    )

                st.success(
                    f"🧠 {len(embeddings)} embeddings "
                    f"created successfully."
                )


                if len(embeddings) > 0:

                    st.write(
                        f"Embedding dimension: "
                        f"{len(embeddings[0])}"
                    )


                # -----------------------------------------
                # 3. VECTOR DATABASE
                # -----------------------------------------

                with st.spinner(
                    "💾 Storing embeddings in ChromaDB..."
                ):

                    store_embeddings(
                        chunks,
                        embeddings,
                        file.name
                    )

                st.success(
                    f"💾 Embeddings from "
                    f"**{file.name}** stored successfully."
                )


            except Exception as e:

                st.error(
                    f"Could not complete RAG processing: {e}"
                )


    # =====================================================
    # DATABASE STATUS
    # =====================================================

    st.divider()

    try:

        total_embeddings = get_collection_count()

        st.info(
            f"📊 Total embeddings stored in the "
            f"vector database: {total_embeddings}"
        )

    except Exception as e:

        st.warning(
            f"Could not read vector database status: {e}"
        )


# =========================================================
# QUESTION ANSWERING
# =========================================================

st.divider()

st.header("🤖 Ask VidyānVaya AI")

st.write(
    "Ask a question based on your uploaded academic materials."
)


query = st.text_input(
    "Enter your question",
    placeholder=(
        "Example: What topics are covered in this document?"
    )
)


if query.strip():

    try:

        # =================================================
        # RETRIEVAL
        # =================================================

        with st.spinner(
            "🔍 Searching your academic materials..."
        ):

            documents = retrieve_relevant_chunks(
                query,
                n_results=5
            )


        # =================================================
        # CHECK RESULTS
        # =================================================

        if not documents:

            st.warning(
                "No relevant information was found "
                "in your uploaded materials."
            )

        else:

            st.success(
                f"🔎 Found {len(documents)} relevant "
                f"text chunks."
            )


            # =================================================
            # BUILD CONTEXT
            # =================================================

            context = "\n\n".join(
                documents
            )


            # =================================================
            # GENERATE ANSWER
            # =================================================

            with st.spinner(
                "🤖 Generating answer..."
            ):

                answer = generate_answer(
                    query,
                    context
                )


            # =================================================
            # DISPLAY ANSWER
            # =================================================

            st.subheader("💡 Answer")

            st.write(answer)


            # =================================================
            # SOURCES
            # =================================================

            with st.expander(
                "📚 View retrieved source information"
            ):

                for index, document in enumerate(
                    documents,
                    start=1
                ):

                    st.markdown(
                        f"### Source {index}"
                    )

                    st.write(document)


    except Exception as e:

        st.error(
            f"Could not retrieve or generate answer: {e}"
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "VidyānVaya AI — AI-powered academic learning assistant"
)
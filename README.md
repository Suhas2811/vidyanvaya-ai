# VidyānVaya AI

### A Subject-Agnostic Academic Learning Assistant

**Official Project:** Subject Guide & Question Bank Assistant AI Agent

> **An Agentic AI-powered academic learning assistant that adapts to different subjects and uses students' uploaded academic materials to provide grounded explanations, question solving, personalized practice, and learning recommendations.**

---

## 📌 Project Overview

VidyānVaya AI is an Agentic AI-based academic learning assistant designed to help students learn from their own academic materials.

Students can upload materials such as:

* Lecture notes
* Textbooks
* Lab manuals
* Previous-year question papers
* Assignments
* Presentation slides
* Syllabus documents

The system processes and organizes these materials and uses a **Multi-Source Retrieval-Augmented Generation (RAG)** approach to provide relevant, source-grounded academic assistance.

The system is designed to be **subject-agnostic**. Instead of being built specifically for one subject such as Computer Science or Mathematics, VidyānVaya AI is designed to adapt to the subject and content provided by each student.

---

## 🎯 Problem Statement

Students often have their learning materials distributed across different sources such as textbooks, lecture notes, laboratory manuals, assignments, and previous-year question papers.

Finding relevant information, understanding topics, solving questions, identifying weak areas, and planning exam preparation can therefore become difficult and time-consuming.

VidyānVaya AI aims to bring these materials together into one intelligent academic learning environment.

---

## 💡 Proposed Solution

VidyānVaya AI is being developed as a unified academic assistant that can:

1. Understand and process multiple academic document formats.
2. Organize information from different sources.
3. Retrieve relevant information from uploaded materials.
4. Explain academic topics using relevant academic sources.
5. Solve questions using relevant study material.
6. Extract questions from previous-year question papers.
7. Support exam preparation workflows.
8. Identify weak areas based on student performance.
9. Provide personalized study recommendations.
10. Track learning progress.

The system initially follows the **Track A foundation** described in the project guide and progressively incorporates selected advanced capabilities inspired by **Track B**, depending on project progress and feasibility.

---

## 🌐 Subject-Agnostic Approach

A major design principle of VidyānVaya AI is **subject independence**.

The system is not hard-coded for a particular academic subject.

Instead, students provide their own academic materials, and the system builds its understanding from those materials.

### Example

A Computer Science student can upload:

* Operating Systems notes
* OS textbook
* Previous-year papers

A Mathematics student can upload:

* Probability notes
* Mathematics textbook
* Question papers

A Mechanical Engineering student can upload:

* Thermodynamics notes
* Textbook
* Previous-year questions

The same application is designed to work with these different academic contexts without requiring subject-specific code changes.

### Core Principle

```text
Student
   ↓
Upload Academic Materials
   ↓
Document Processing
   ↓
Content Understanding
   ↓
Multi-Source RAG
   ↓
Academic AI Assistant
   ↓
Explain / Solve / Practice / Assess / Recommend
```

---

# 🚀 Current & Planned Features

## 1. Multi-Document Upload

VidyānVaya AI currently supports academic materials in multiple formats:

* PDF
* DOCX
* PPTX

The uploaded documents are processed and converted into text before entering the RAG pipeline.

---

## 2. Document Processing

The document-processing layer handles different academic file formats.

### Processing Flow

```text
Academic Document
       ↓
PDF / DOCX / PPTX
       ↓
Text Extraction
       ↓
Text Processing
       ↓
Chunking
       ↓
Embeddings
```

The system is designed to work with multiple academic documents rather than a single fixed subject or document.

---

## 3. OCR for Scanned PDFs

Many university question papers are scanned PDFs without a machine-readable text layer.

VidyānVaya AI now supports OCR-based extraction for such documents.

### OCR Flow

```text
Scanned PDF
     ↓
Check for Text Layer
     ↓
Text Available?
   ↙       ↘
 Yes        No
  ↓          ↓
Text      Render Page
Extraction     ↓
           Tesseract OCR
               ↓
          Extracted Text
```

### OCR Technologies

* PyMuPDF
* Tesseract OCR
* pytesseract

This allows scanned question papers to be processed and passed to the Question Bank pipeline.

---

## 4. Multi-Source RAG

VidyānVaya AI uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant academic information before generating an AI response.

### RAG Pipeline

```text
Academic Documents
        ↓
Text Extraction
        ↓
Text Chunking
        ↓
Sentence Transformer Embeddings
        ↓
ChromaDB
        ↓
Semantic Retrieval
        ↓
Relevant Academic Chunks
        ↓
LLM
        ↓
Grounded Response
```

The RAG system supports document-specific retrieval so that responses can be grounded in the selected academic material.

---

## 5. Subject Guide

Students can ask questions about their uploaded academic materials.

Example:

> "Explain this topic with examples."

The system retrieves relevant academic content and generates a structured explanation.

### Subject Guide Workflow

```text
Student Question
       ↓
Semantic Retrieval
       ↓
Relevant Academic Chunks
       ↓
Academic Context
       ↓
AI Provider
       ↓
Student-Friendly Explanation
       ↓
Academic Sources
```

The system is designed to use uploaded academic material as the primary source for:

* Definitions
* Concepts
* Formulas
* Methods
* Examples
* Explanations
* Numerical problem solving

---

## 6. Question Bank

VidyānVaya AI now includes an AI-powered **Question Bank** module.

The system can process examination papers and extract individual questions from them.

### Question Bank Workflow

```text
Question Paper
       ↓
PDF Text Extraction
       ↓
OCR if Required
       ↓
Question Paper Text
       ↓
AI Question Extraction
       ↓
Structured Question List
       ↓
Question Bank
```

The question extraction system is designed to:

* Extract actual questions
* Preserve question numbering
* Preserve question wording as closely as possible
* Keep sub-parts together
* Avoid combining separate questions
* Avoid inventing questions
* Ignore page numbers and unrelated document content

### Example

```text
Q1

a) Describe the bus structure of a computer.
b) Derive the basic performance equation of a computer.

Q2

a) Define the processor clock.
b) Explain different addressing modes.
```

---

## 7. AI Question Solver

The Question Solver allows students to select a question from the extracted Question Bank and generate an exam-oriented solution using relevant academic material.

### Question Solver Workflow

```text
Extracted Question
       ↓
Student Selects Question
       ↓
Select Academic Material
       ↓
Semantic Retrieval
       ↓
Relevant Academic Chunks
       ↓
AI Question Solver
       ↓
Structured Solution
       ↓
Academic Sources
```

The solver supports:

* Definitions
* Conceptual questions
* Descriptive questions
* Multi-part questions
* Formula-based questions
* Numerical problems
* Step-by-step explanations
* Exam-oriented answers
* Academic source display

The system retrieves relevant academic chunks before generating the solution.

---

## 8. Multi-LLM Provider Architecture

VidyānVaya AI supports multiple AI providers through a common provider layer.

This architecture provides flexibility and allows the system to use a fallback provider when a qualifying provider failure occurs.

### Provider Architecture

```text
                 AI Provider Layer
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
       Gemini         OpenAI        Ollama
          │             │             │
          └─────────────┼─────────────┘
                        ↓
                   AI Response
```

### Provider Priority

```text
Gemini
   ↓
OpenAI
   ↓
Ollama
```

### Supported Providers

* Google Gemini
* OpenAI
* Ollama

---

## 9. Local LLM Support

VidyānVaya AI also supports local language-model inference through Ollama.

The currently configured local model is:

```text
Qwen3 4B
```

Ollama provides an additional local AI option alongside cloud-based providers.

---

## 10. Question Practice

Topic-wise practice question generation is part of the planned learning workflow.

Future versions will allow students to generate practice questions based on:

* Subject
* Topic
* Difficulty
* Academic material
* Previous question patterns

Planned question types include:

* Multiple-choice questions
* Short-answer questions
* Descriptive questions
* Topic-based practice

---

## 11. Exam Preparation Assistant

The system is planned to support exam-oriented learning workflows such as:

```text
Theory
   ↓
Examples
   ↓
Practice
   ↓
Assessment
   ↓
Revision
```

The goal is to help students move from understanding a topic to practicing and revising it for examinations.

---

## 12. Weak-Area Identification

A future learning-analytics module will analyze question-practice performance to identify topics where the student may need additional practice.

---

## 13. Personalized Recommendations

Based on student progress, the system will eventually recommend:

* Topics to revise
* Relevant study material
* Questions to practice
* Suggested learning sequence

---

## 14. Progress Tracking

Future versions will maintain learning-related information such as:

* Topics attempted
* Questions attempted
* Performance
* Weak areas
* Learning progress

---

## 15. Agentic Assistance

An agentic layer is planned to determine the student's intent and select the appropriate academic capability.

The planned architecture is:

```text
User Query
    ↓
AI Agent / Query Router
    │
    ├── Topic Explanation
    │
    ├── Question Solving
    │
    ├── Practice Generation
    │
    ├── Performance Analysis
    │
    └── Study Recommendation
```

The current implementation focuses on building the reliable document-processing, RAG, Question Bank, and Question Solver foundation before expanding the agentic layer.

---

# 🏗️ Current System Architecture

```text
                         STUDENT
                            │
                            ▼
                    ┌─────────────────┐
                    │   Streamlit UI  │
                    └────────┬────────┘
                             │
                             ▼
                  Academic Documents
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
            PDF             DOCX            PPTX
             │
             ▼
      Text Extraction
             │
             ▼
        OCR Fallback
             │
             ▼
          Chunking
             │
             ▼
        Embeddings
             │
             ▼
          ChromaDB
             │
             ▼
     Semantic Retrieval
             │
       ┌─────┴─────┐
       │           │
       ▼           ▼
 Academic Q&A   Question Bank
       │           │
       │           ▼
       │      Question Extraction
       │           │
       │           ▼
       │      Question Selection
       │           │
       └─────┬─────┘
             │
             ▼
      Academic Context
             │
             ▼
       AI Provider Layer
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
    Gemini OpenAI Ollama
             │
             ▼
       AI Response
             │
             ▼
      Academic Sources
```

---

# 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| AI / LLM Framework | LangChain |
| User Interface | Streamlit |
| PDF Processing | PyMuPDF |
| DOCX Processing | python-docx |
| PPTX Processing | python-pptx |
| OCR | Tesseract OCR |
| OCR Python Interface | pytesseract |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| Cloud LLM | Google Gemini |
| Cloud LLM | OpenAI |
| Local LLM | Ollama |
| Local Model | Qwen3 4B |
| Environment Configuration | python-dotenv |
| Version Control | Git + GitHub |

The technology stack may evolve during development if a different tool provides better performance, reliability, or scalability.

---

# 📁 Project Structure

```text
vidyanvaya-ai/
│
├── agents/
│
├── app/
│   └── main.py
│
├── data/
│
├── document_processing/
│   ├── __init__.py
│   ├── docx_processor.py
│   ├── pdf_processor.py
│   └── pptx_processor.py
│
├── rag/
│   ├── chunking.py
│   ├── embeddings.py
│   ├── retrieval.py
│   └── vector_store.py
│
├── services/
│   ├── ai_provider.py
│   ├── llm_service.py
│   ├── ollama_service.py
│   ├── openai_service.py
│   └── question_bank_service.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 📅 8-Week Development Roadmap

## Week 1 — Foundation & Project Setup

### Completed ✅

* Finalized project architecture.
* Set up the development environment.
* Configured Python and Streamlit.
* Established the application structure.
* Implemented the document-processing foundation.
* Defined the data flow for the subject-agnostic system.

### Outcome

A working application foundation capable of accepting academic documents.

---

## Week 2 — Multi-Source RAG

### Completed ✅

* Implemented PDF, DOCX and PPTX processing.
* Extracted academic content.
* Split documents into meaningful chunks.
* Generated embeddings.
* Implemented ChromaDB vector storage.
* Implemented semantic retrieval.
* Added multi-document support.

### Outcome

The system can retrieve relevant information from uploaded academic documents.

---

## Week 3 — Subject Guide

### Completed ✅

* Implemented topic/question-based retrieval.
* Generated academic explanations using retrieved context.
* Added source-aware responses.
* Implemented document-specific retrieval.
* Improved document isolation.
* Improved RAG reliability.

### Outcome

Students can ask questions about uploaded academic materials and receive grounded responses.

---

## Week 4 — Question Bank & Question Solver

### Completed ✅

* Processed previous-year question papers.
* Added OCR support for scanned PDFs.
* Implemented automatic question extraction.
* Created a structured Question Bank.
* Added question selection.
* Connected questions with relevant study material.
* Implemented semantic retrieval for selected questions.
* Implemented AI-powered Question Solver.
* Added structured exam-oriented solutions.
* Added academic source display.
* Added multi-LLM provider architecture.
* Added provider fallback mechanism.
* Added Ollama local LLM support.

### Validation

A scanned Computer Organization and Architecture question paper was used to validate the workflow.

The system successfully:

```text
Scanned Question Paper
        ↓
       OCR
        ↓
Text Extraction
        ↓
Question Extraction
        ↓
10 Questions
        ↓
Question Selection
        ↓
Academic Retrieval
        ↓
8 Relevant Chunks
        ↓
AI Question Solver
        ↓
Structured Solution
        ↓
Academic Sources
```

### Outcome

The system can extract questions from examination papers and solve selected questions using relevant uploaded academic material.

---

## Week 5 — Exam Preparation Assistant

### Planned 🔄

### Objectives

* Create topic-wise practice workflows.
* Support syllabus-based exam preparation.
* Provide targeted question practice.
* Organize learning into theory, examples, practice and assessment.
* Improve question selection based on topic and difficulty.

### Expected Outcome

The system begins functioning as a personalized exam-preparation assistant.

---

## Week 6 — Personalized Learning & Analytics

### Planned 🔄

### Objectives

* Track question-practice performance.
* Identify weak topics.
* Recommend relevant study materials.
* Generate personalized study recommendations.
* Create basic learning-progress tracking.
* Develop personalized study-plan functionality.

### Expected Outcome

The system can use student performance to provide more targeted academic guidance.

---

## Week 7 — Agentic Intelligence & Advanced Features

### Planned 🔄

### Objectives

* Improve the agent/query-routing layer.
* Introduce intelligent tool selection.
* Explore adaptive explanation levels.
* Explore intelligent learning-path generation.
* Improve topic-question relationships.
* Enhance the academic dashboard and user experience.

Selected advanced capabilities from the Track B direction will be implemented based on the stability and progress of the core system.

### Expected Outcome

A more intelligent and personalized academic assistant with stronger agentic behavior.

---

## Week 8 — Testing, Deployment & Finalization

### Planned 🔄

### Objectives

* Test the system with different academic subjects.
* Test multiple document types.
* Improve response accuracy and reliability.
* Add input validation and error handling.
* Finalize the user interface.
* Deploy the application.
* Complete README and technical documentation.
* Prepare the final demonstration.
* Prepare the final presentation.

### Expected Outcome

A deployed, polished, subject-agnostic academic AI assistant suitable for demonstration and portfolio use.

---

# 🔄 Track A → Advanced Track Strategy

The project initially follows the **Track A foundation** to ensure that the core academic RAG functionality is reliable and achievable within the project timeline.

After the core system is stable, selected advanced capabilities will be introduced progressively.

Potential advanced capabilities include:

* Intelligent agent routing
* Adaptive explanations
* Learning-path generation
* Topic-question mapping
* Learning analytics
* Personalized recommendations
* Knowledge relationships between topics

The exact advanced features will be finalized based on project progress and feasibility.

---

# 🧪 Evaluation

The system will be evaluated using academic materials from multiple subject areas.

Current validation has focused on the core Week 4 pipeline, including scanned question-paper processing, OCR, question extraction, retrieval, and question solving.

Future evaluation will focus on:

* Multi-document retrieval quality
* Relevance of retrieved content
* Accuracy of explanations
* Quality of question solutions
* Question-generation quality
* Subject adaptability
* Personalization effectiveness
* User experience
* Application reliability

The system will ideally be demonstrated using multiple academic subjects to validate its subject-agnostic design.

---

# 📊 Week 4 Validation Results

| Feature | Status |
|---|---|
| PDF Processing | ✅ |
| DOCX Processing | ✅ |
| PPTX Processing | ✅ |
| Scanned PDF OCR | ✅ |
| Question Extraction | ✅ |
| Question Bank | ✅ |
| Question Selection | ✅ |
| Semantic Retrieval | ✅ |
| Document-Specific Retrieval | ✅ |
| AI Question Solver | ✅ |
| Structured Solutions | ✅ |
| Academic Sources | ✅ |
| Gemini Integration | ✅ |
| Multi-LLM Fallback | ✅ |
| Ollama Integration | ✅ |

---

# 📌 Expected Final Outcome

The final goal is to develop **VidyānVaya AI**, a subject-agnostic Agentic AI academic learning assistant that can transform a student's own academic materials into an interactive learning environment.

The completed system is expected to support:

```text
UPLOAD
   ↓
UNDERSTAND
   ↓
ASK
   ↓
LEARN
   ↓
SOLVE
   ↓
PRACTICE
   ↓
ASSESS
   ↓
IMPROVE
```

The project prioritizes reliable multi-source academic retrieval and grounded responses first, followed by personalization and advanced agentic capabilities.

---

# 🔮 Future Scope

Future development may include:

* Support for additional document formats
* Advanced OCR capabilities
* Advanced knowledge graphs
* Adaptive learning
* Mobile application
* LMS integration
* Advanced learning analytics
* Multi-language academic support
* Personalized tutoring
* Scalable cloud architecture

---

# 📌 Development Status

## Current Status: Week 4 Completed ✅

### Completed

* Project foundation
* Streamlit application
* PDF processing
* DOCX processing
* PPTX processing
* OCR for scanned PDFs
* Text chunking
* Sentence Transformer embeddings
* ChromaDB vector storage
* Semantic retrieval
* Document-specific retrieval
* Subject Guide / Academic Q&A
* Question Paper processing
* AI Question extraction
* Question Bank
* Question selection
* AI Question Solver
* Exam-oriented solutions
* Academic source display
* Gemini integration
* Multi-LLM provider layer
* Provider fallback mechanism
* Ollama local LLM support

### Upcoming

* Examination preparation workflows
* Topic-wise practice
* Weak-area identification
* Personalized recommendations
* Progress tracking
* Advanced agentic routing
* UI improvements
* Deployment
* Final testing and documentation

---

# 📄 Project Information

| Field | Details |
|---|---|
| Project | VidyānVaya AI |
| Official Project | Subject Guide & Question Bank Assistant AI Agent |
| Development Approach | Track A Foundation → Selected Advanced Capabilities |
| Duration | 8 Weeks |
| Current Stage | Week 4 Completed |
| Domain | Educational Technology / Academic Learning |
| Architecture | Multi-Source RAG + Multi-LLM + Planned Agentic Layer |
| Primary Interface | Streamlit |
| Repository | GitHub |

---

# 🎓 Project Vision

VidyānVaya AI aims to evolve from an academic question-answering system into a complete AI-powered learning assistant.

The long-term vision is to help students move through the complete learning cycle:

```text
Learn
  ↓
Understand
  ↓
Practice
  ↓
Solve
  ↓
Identify Weak Areas
  ↓
Revise
  ↓
Prepare for Exams
```

The project will continue to prioritize grounded academic assistance using the student's own learning materials while progressively introducing personalized and agentic capabilities.

---

# 👨‍💻 Author

**Suhas Subramani**

Computer Science & Engineering — Data Science

---

## ⭐ Project

If you find VidyānVaya AI useful or interesting, consider giving the repository a ⭐.

**VidyānVaya AI — Learn from your materials. Solve with AI.**

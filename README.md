# 📚 VidyānVaya AI

### A Subject-Agnostic Academic Learning Assistant

**Official Project:** Subject Guide & Question Bank Assistant AI Agent

> **An Agentic AI-powered academic learning assistant that adapts to different subjects and uses students' uploaded academic materials to provide grounded explanations, question solving, personalized practice, performance analysis, and learning recommendations.**

---

# 🌐 Project Links

### 🚀 Live Application

https://vidyanvaya-ai.streamlit.app/

### 💻 GitHub Repository

https://github.com/Suhas2811/vidyanvaya-ai


---

# 📌 Project Overview

VidyānVaya AI is an Agentic AI-based academic learning assistant designed to help students learn from their own academic materials.

Students can upload materials such as:

- Lecture notes
- Textbooks
- Lab manuals
- Previous-year question papers
- Assignments
- Presentation slides
- Syllabus documents

The system processes and organizes these materials and uses a **Multi-Source Retrieval-Augmented Generation (RAG)** approach to provide relevant, source-grounded academic assistance.

The system is designed to be **subject-agnostic**. Instead of being built specifically for one subject such as Computer Science or Mathematics, VidyānVaya AI is designed to adapt to the subject and content provided by each student.

---

# 🎯 Problem Statement

Students often have their learning materials distributed across different sources such as textbooks, lecture notes, laboratory manuals, assignments, and previous-year question papers.

Finding relevant information, understanding topics, solving questions, practicing for examinations, identifying weak areas, and planning exam preparation can become difficult and time-consuming.

VidyānVaya AI aims to bring these materials together into one intelligent academic learning environment.

---

# 💡 Proposed Solution

VidyānVaya AI is a unified academic assistant that can:

1. Process multiple academic document formats.
2. Organize information from different academic sources.
3. Retrieve relevant information from uploaded materials.
4. Explain academic topics using relevant academic sources.
5. Solve questions using relevant study material.
6. Extract questions from previous-year question papers.
7. Generate exam-oriented practice tests.
8. Evaluate student answers.
9. Analyze student performance.
10. Identify weak and strong academic areas.
11. Provide personalized study recommendations.
12. Support an iterative learning and exam-preparation workflow.

The project initially focused on establishing a reliable RAG foundation and progressively added question solving, exam preparation, performance analysis, and personalization capabilities.

---

# 🌐 Subject-Agnostic Approach

A major design principle of VidyānVaya AI is **subject independence**.

The system is not hard-coded for a particular academic subject.

Instead, students provide their own academic materials, and the system builds its understanding from those materials.

### Example

A Computer Science student can upload:

- Operating Systems notes
- OS textbook
- Previous-year papers

A Mathematics student can upload:

- Probability notes
- Mathematics textbook
- Question papers

A Mechanical Engineering student can upload:

- Thermodynamics notes
- Textbook
- Previous-year questions

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
Explain / Solve / Practice / Assess / Analyze / Recommend
```

---

# 🚀 Current Features

## 1. 📄 Multi-Document Upload

VidyānVaya AI supports academic materials in multiple formats:

- PDF
- DOCX
- PPTX

The uploaded documents are processed and converted into text before entering the RAG pipeline.

---

## 2. 📑 Document Processing

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
       ↓
Vector Storage
```

The system is designed to work with multiple academic documents rather than a single fixed subject or document.

---

## 3. 🔎 OCR for Scanned PDFs

Many university question papers are scanned PDFs without a machine-readable text layer.

VidyānVaya AI supports OCR-based extraction for such documents.

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

- PyMuPDF
- Tesseract OCR
- pytesseract

This allows scanned question papers to be processed and passed to the Question Bank pipeline.

---

## 4. 🧠 Multi-Source Retrieval-Augmented Generation

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
AI Provider
        ↓
Grounded Response
```

The RAG system supports document-specific retrieval so that responses can be grounded in the selected academic material.

---

## 5. 💬 Subject Guide / Academic Q&A

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

- Definitions
- Concepts
- Formulas
- Methods
- Examples
- Explanations
- Numerical problem solving

---

## 6. 📝 AI Question Bank

VidyānVaya AI includes an AI-powered **Question Bank** module.

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

- Extract actual questions
- Preserve question numbering
- Preserve question wording as closely as possible
- Keep sub-parts together
- Avoid combining separate questions
- Avoid inventing questions
- Ignore page numbers and unrelated document content

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

## 7. 🧠 AI Question Solver

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

- Definitions
- Conceptual questions
- Descriptive questions
- Multi-part questions
- Formula-based questions
- Numerical problems
- Step-by-step explanations
- Exam-oriented answers
- Academic source display

The system retrieves relevant academic chunks before generating the solution.

---

## 8. 🤖 Multi-LLM Provider Architecture

VidyānVaya AI supports multiple AI providers through a common provider layer.

This architecture provides flexibility and allows the system to fall back to another provider when a provider is unavailable.

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

- Google Gemini
- OpenAI
- Ollama

---

## 9. 🖥️ Local LLM Support

VidyānVaya AI also supports local language-model inference through Ollama.

The currently configured local model is:

```text
Qwen3 4B
```

Ollama provides an additional local AI option alongside cloud-based providers.

---

## 10. 📝 AI Exam Preparation

VidyānVaya AI includes an exam-preparation workflow that allows students to generate practice tests from uploaded academic materials.

Students can configure:

- Academic material
- Topic
- Difficulty level
- Number of questions

### Practice Test Workflow

```text
Select Academic Material
        ↓
Select Topic
        ↓
Select Difficulty
        ↓
Select Number of Questions
        ↓
Retrieve Relevant Academic Content
        ↓
Generate Practice Questions
        ↓
Student Answers Questions
```

The generated questions are designed to be based primarily on the uploaded academic material.

---

## 11. ✍️ AI Answer Evaluation

Students can submit their answers to generated practice questions.

VidyānVaya AI evaluates the answer against the question and relevant academic material.

The evaluation includes:

- Correct / Partially Correct / Incorrect result
- Score out of 10
- Feedback
- Missing points
- Ideal answer

### Evaluation Workflow

```text
Practice Question
       ↓
Student Answer
       ↓
Academic Context
       ↓
AI Evaluation
       ↓
Score + Feedback
       ↓
Missing Points
       ↓
Ideal Answer
```

---

## 12. 📊 Performance Analysis

VidyānVaya AI includes a performance-analysis module that uses practice-test results to understand student performance.

The system calculates:

- Total tests attempted
- Total score
- Total marks
- Overall percentage
- Topic-wise performance

The system also identifies:

- Weak areas
- Strong areas
- Areas requiring additional practice

### Performance Analysis Workflow

```text
Practice Test
       ↓
Student Answers
       ↓
AI Evaluation
       ↓
Score Calculation
       ↓
Performance History
       ↓
Topic-wise Analysis
       ↓
Weak / Strong Area Detection
       ↓
Personalized Recommendations
```

---

## 13. 💡 Personalized Study Recommendations

Based on student performance, VidyānVaya AI generates recommendations for further study.

Example:

```text
Weak Area:
Computer Organization — 45%

Recommendation:
Review the core concepts and practice more questions.
```

This creates a personalized learning loop:

```text
Study
  ↓
Practice
  ↓
Answer
  ↓
Evaluation
  ↓
Performance Analysis
  ↓
Weak Area Detection
  ↓
Study Recommendation
  ↓
Practice Again
```

---

## 14. 📈 Topic-Wise Performance

The performance-analysis module groups practice-test results by topic.

For example:

```text
Computer Organization → 45%
Operating Systems     → 90%
```

This allows the system to distinguish between areas where the student may need additional practice and areas where the student has demonstrated stronger performance.

---

## 15. 🔎 Weak-Area Detection

The system analyzes topic-wise performance and identifies topics below the configured performance threshold.

Example:

```text
Weak Areas
----------------------------
Computer Organization
Performance: 45%
```

The purpose is to help students focus their revision on areas that require additional practice.

---

## 16. ⭐ Strong-Area Detection

The system also identifies topics where the student's performance is stronger.

Example:

```text
Strong Areas
----------------------------
Operating Systems
Performance: 90%
```

This provides a more complete view of student performance rather than focusing only on weaknesses.

---

## 17. 📚 Personalized Learning Loop

The current system connects learning, practice, evaluation, and performance analysis.

```text
Upload Materials
       ↓
Learn from Materials
       ↓
Ask Questions
       ↓
Solve Questions
       ↓
Generate Practice Test
       ↓
Submit Answers
       ↓
AI Evaluation
       ↓
Performance Analysis
       ↓
Weak / Strong Area Detection
       ↓
Personalized Recommendation
       ↓
Targeted Revision
```

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
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
              PDF           DOCX          PPTX
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
       ┌───────┴────────┐
       │                │
       ▼                ▼
 Academic Q&A      Question Bank
       │                │
       │                ▼
       │         Question Extraction
       │                │
       │                ▼
       │         Question Selection
       │                │
       └───────┬────────┘
               │
               ▼
       Academic Context
               │
               ▼
       AI Provider Layer
               │
        ┌──────┼──────┐
        ▼      ▼      ▼
     Gemini  OpenAI  Ollama
               │
               ▼
          AI Response
               │
               ▼
       Academic Sources
               │
               ▼
      Exam Preparation
               │
               ▼
        Practice Test
               │
               ▼
       Answer Evaluation
               │
               ▼
      Performance Analysis
               │
               ▼
   Weak / Strong Area Detection
               │
               ▼
      Study Recommendations
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
| Additional Cloud LLM | OpenAI |
| Local LLM | Ollama |
| Local Model | Qwen3 4B |
| Environment Configuration | python-dotenv |
| Version Control | Git + GitHub |

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
│   ├── exam_prep_service.py
│   ├── llm_service.py
│   ├── ollama_service.py
│   ├── openai_service.py
│   ├── performance_service.py
│   └── question_bank_service.py
│
├── tests/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Suhas2811/vidyanvaya-ai.git
cd vidyanvaya-ai
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

Do not commit actual API keys to GitHub.

The `.env` file should remain excluded through `.gitignore`.

OpenAI is an optional provider in the multi-provider architecture. The application can continue with the available fallback providers when OpenAI is unavailable.

---

# 🖥️ Ollama Setup

Ollama is optional.

If you want to use the local LLM provider, install Ollama and pull the configured model:

```bash
ollama pull qwen3:4b
```

Verify the installed model:

```bash
ollama list
```

---

# 🔤 Tesseract OCR Setup

Tesseract OCR is required for scanned/image-based PDFs.

On Windows, install Tesseract OCR and ensure the executable is available to the application.

Verify the installation:

```powershell
tesseract --version
```

If Tesseract is not available through the system PATH, configure the installed executable path as required by the application.

---

# ▶️ Running the Application

Start the Streamlit application with:

```bash
streamlit run app/main.py
```

The application will open in the browser.

---

# 🧪 Validation & Testing

The project has been tested across multiple workflows during development.

## Document Processing

- PDF processing
- DOCX processing
- PPTX processing
- Scanned PDF OCR

## RAG

- Semantic retrieval
- Document-specific retrieval
- ChromaDB storage
- Academic context-based responses
- Document isolation

## Question Bank

- Question-paper processing
- OCR-based question extraction
- Individual question extraction
- Question numbering preservation
- Sub-question preservation
- Structured JSON validation

## Question Solver

- Question selection
- Relevant academic retrieval
- AI-generated solutions
- Exam-oriented responses
- Source/context display

## Exam Preparation

- Practice-question generation
- Topic selection
- Difficulty selection
- Configurable question count
- Student answer submission
- AI answer evaluation
- Score generation
- Feedback generation
- Ideal-answer generation

## Performance Analysis

- Overall performance calculation
- Topic-wise performance
- Weak-area identification
- Strong-area identification
- Personalized study recommendations

## Multi-LLM

- Gemini provider
- OpenAI provider architecture
- Ollama provider
- Provider fallback mechanism

---

# 🧪 Week 4 Validation

A scanned Computer Organization and Architecture question paper was used to validate the question-paper workflow.

The system successfully performed:

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

### Week 4 Validation Result

The system successfully extracted questions from the scanned question paper and generated an academic solution for a selected question using relevant retrieved study material.

---

# 🧪 Week 5 Validation

The Week 5 exam-preparation workflow was validated using uploaded academic material.

The system successfully performed:

```text
Academic Material
       ↓
Topic Selection
       ↓
Difficulty Selection
       ↓
Practice Test Generation
       ↓
Student Answers
       ↓
AI Answer Evaluation
       ↓
Score
       ↓
Feedback
       ↓
Ideal Answer
```

The answer-evaluation workflow successfully generated:

- Result classification
- Score
- Feedback
- Missing points
- Ideal answer

---

# 🧪 Week 6 Validation

The Week 6 performance-analysis module was tested with practice-test performance data.

The system successfully demonstrated:

```text
Practice-Test Results
        ↓
Overall Performance
        ↓
Topic-Wise Analysis
        ↓
Weak Area Detection
        ↓
Strong Area Detection
        ↓
Personalized Recommendation
```

The performance-analysis service successfully calculated overall and topic-wise percentages and generated recommendations for weaker areas.

---

# 📅 8-Week Development Roadmap

## Week 1 — Foundation & Project Setup

### Status: ✅ Completed

- Finalized project architecture
- Set up the development environment
- Configured Python and Streamlit
- Established the application structure
- Implemented the document-processing foundation
- Defined the data flow for the subject-agnostic system

### Outcome

A working application foundation capable of accepting academic documents.

---

## Week 2 — Multi-Source RAG

### Status: ✅ Completed

- Implemented PDF, DOCX and PPTX processing
- Extracted academic content
- Split documents into meaningful chunks
- Generated embeddings
- Implemented ChromaDB vector storage
- Implemented semantic retrieval
- Added multi-document support

### Outcome

The system can retrieve relevant information from uploaded academic documents.

---

## Week 3 — Subject Guide

### Status: ✅ Completed

- Implemented topic/question-based retrieval
- Generated academic explanations using retrieved context
- Added source-aware responses
- Implemented document-specific retrieval
- Improved document isolation
- Improved RAG reliability

### Outcome

Students can ask questions about uploaded academic materials and receive grounded responses.

---

## Week 4 — Question Bank & Question Solver

### Status: ✅ Completed

- Processed previous-year question papers
- Added OCR support for scanned PDFs
- Implemented automatic question extraction
- Created a structured Question Bank
- Added question selection
- Connected questions with relevant study material
- Implemented semantic retrieval for selected questions
- Implemented AI-powered Question Solver
- Added structured exam-oriented solutions
- Added academic source display
- Added multi-LLM provider architecture
- Added provider fallback mechanism
- Added Ollama local LLM support

### Outcome

The system can extract questions from examination papers and solve selected questions using relevant uploaded academic material.

---

## Week 5 — Exam Preparation Assistant

### Status: ✅ Completed

- Implemented AI-generated practice tests
- Added topic selection
- Added difficulty selection
- Added configurable question count
- Added academic-material-based question generation
- Added student answer submission
- Implemented AI answer evaluation
- Added Correct / Partially Correct / Incorrect classification
- Added score generation
- Added feedback generation
- Added missing-point identification
- Added ideal-answer generation

### Outcome

The system can now function as an exam-preparation assistant by generating practice tests from uploaded academic materials and evaluating student answers.

---

## Week 6 — Performance Analysis & Personalized Recommendations

### Status: ✅ Completed

- Implemented practice-test performance tracking
- Implemented overall score calculation
- Implemented overall percentage calculation
- Implemented topic-wise performance analysis
- Implemented weak-area detection
- Implemented strong-area detection
- Implemented personalized study recommendations
- Integrated performance tracking with the exam-preparation workflow
- Tested the performance-analysis service
- Tested the complete practice-test evaluation flow

### Outcome

The system has progressed from evaluating individual answers to analyzing student performance and providing personalized academic guidance.

---

## Week 7 — UI, Integration & Refinement

### Status: ✅ Completed

Week 7 focused on bringing all implemented modules together into a polished and unified academic learning platform.

### Completed Work

- Improved the overall Streamlit UI/UX
- Integrated the major modules into a unified workflow
- Improved navigation
- Improved section organization
- Improved visual consistency
- Improved performance-result presentation
- Improved weak-area and recommendation displays
- Added performance visualizations where appropriate
- Improved the overall student experience
- Tested complete end-to-end workflows
- Fixed integration issues and edge cases
- Improved application stability
- Improved usability
- Refined the interface for the final demonstration

### Outcome

A unified and polished VidyānVaya AI application in which document processing, RAG, Question Bank, Question Solver, Exam Preparation, and Performance Analysis work together as a cohesive learning platform.

---

## Week 8 — Deployment & Finalization

### Status: ✅ Completed

The final week focused on preparing VidyānVaya AI for deployment, demonstration, documentation, and final submission.

### Completed Work

- Final application testing
- End-to-end testing
- Bug fixing
- Performance and reliability improvements
- Deployment to Streamlit Community Cloud
- Final README and documentation updates
- Project presentation preparation
- Final demonstration recording
- Final project submission

### Outcome

A deployed and polished subject-agnostic academic AI learning assistant ready for demonstration and submission.

### Deployment

The final application is publicly available at:

https://vidyanvaya-ai.streamlit.app/


---

# 🔄 Development Progress

| Week | Focus | Status |
|---|---|---|
| Week 1 | Foundation & Document Processing | ✅ Completed |
| Week 2 | Multi-Source RAG | ✅ Completed |
| Week 3 | Subject Guide & Academic Q&A | ✅ Completed |
| Week 4 | Question Bank & Question Solver | ✅ Completed |
| Week 5 | Exam Preparation Assistant | ✅ Completed |
| Week 6 | Performance Analysis & Recommendations | ✅ Completed |
| Week 7 | UI, Integration & Refinement | ✅ Completed |
| Week 8 | Deployment & Finalization | ✅ Completed |

---

# 📊 Current Project Capabilities

VidyānVaya AI currently supports the following major workflow:

```text
                UPLOAD
                   ↓
        Academic Documents
                   ↓
          DOCUMENT PROCESSING
                   ↓
              OCR if needed
                   ↓
              CHUNKING
                   ↓
             EMBEDDINGS
                   ↓
              CHROMADB
                   ↓
        SEMANTIC RETRIEVAL
                   ↓
          ACADEMIC CONTEXT
                   ↓
              AI PROVIDER
                   ↓
       ┌───────────┴───────────┐
       ↓                       ↓
  SUBJECT GUIDE          QUESTION BANK
       ↓                       ↓
   EXPLANATION          QUESTION SOLVER
                               ↓
                       EXAM PREPARATION
                               ↓
                        PRACTICE TEST
                               ↓
                       ANSWER EVALUATION
                               ↓
                      PERFORMANCE ANALYSIS
                               ↓
                   WEAK / STRONG AREAS
                               ↓
                  PERSONALIZED RECOMMENDATION
```

---

# 📊 Feature Status

| Feature | Status |
|---|---|
| PDF Processing | ✅ Completed |
| DOCX Processing | ✅ Completed |
| PPTX Processing | ✅ Completed |
| Scanned PDF OCR | ✅ Completed |
| Text Chunking | ✅ Completed |
| Sentence Transformer Embeddings | ✅ Completed |
| ChromaDB Vector Storage | ✅ Completed |
| Semantic Retrieval | ✅ Completed |
| Document-Specific Retrieval | ✅ Completed |
| Subject Guide / Academic Q&A | ✅ Completed |
| Question Paper Processing | ✅ Completed |
| AI Question Extraction | ✅ Completed |
| Question Bank | ✅ Completed |
| Question Selection | ✅ Completed |
| AI Question Solver | ✅ Completed |
| Structured Solutions | ✅ Completed |
| Academic Sources | ✅ Completed |
| Gemini Integration | ✅ Completed |
| OpenAI Provider Support | ✅ Implemented |
| Ollama Integration | ✅ Completed |
| Multi-LLM Fallback | ✅ Completed |
| Practice Test Generation | ✅ Completed |
| Topic Selection | ✅ Completed |
| Difficulty Selection | ✅ Completed |
| Student Answer Submission | ✅ Completed |
| AI Answer Evaluation | ✅ Completed |
| Score Generation | ✅ Completed |
| Feedback Generation | ✅ Completed |
| Ideal Answer Generation | ✅ Completed |
| Performance Tracking | ✅ Completed |
| Topic-Wise Performance | ✅ Completed |
| Weak-Area Detection | ✅ Completed |
| Strong-Area Detection | ✅ Completed |
| Personalized Recommendations | ✅ Completed |
| Unified UI Refinement | ✅ Completed |
| Advanced Visualizations | ✅ Completed |
| Deployment | ✅ Completed |
| Final Documentation | ✅ Completed |

---

# 🔮 Future Enhancements

Potential future improvements include:

- Persistent student performance history
- Progress tracking across multiple practice sessions
- Performance-over-time graphs
- More advanced recommendation algorithms
- Topic-level learning paths
- Intelligent study planning
- Intelligent query routing
- Adaptive explanation levels
- Intelligent learning-path generation
- Additional AI providers
- More document formats
- Advanced analytics dashboard
- Advanced agentic workflows
- Production deployment

These enhancements will be introduced based on project requirements, stability, and feasibility.

---

# 🔐 Security Notes

- API keys should be stored in `.env`.
- `.env` should never be committed to GitHub.
- Uploaded academic materials should be handled carefully.
- API credentials should not be exposed in source code.
- Local development data and vector databases should not be unnecessarily committed to the repository.

---

# 🎓 Intended Users

VidyānVaya AI is primarily designed for students who want to:

- Study from their own academic materials
- Understand difficult concepts
- Ask questions about their notes and textbooks
- Practice university-style questions
- Solve previous-year question papers
- Generate practice tests
- Evaluate their answers
- Identify weak areas
- Receive personalized study recommendations
- Improve their exam preparation

---

# 🚀 Project Vision

VidyānVaya AI is being developed as a subject-agnostic academic learning assistant that goes beyond simple question answering.

The long-term vision is to create an intelligent learning environment where the system can understand a student's academic materials, help them learn, generate practice questions, evaluate their answers, analyze their performance, and guide them toward areas that need improvement.

The overall learning cycle is:

```text
Learn
  ↓
Understand
  ↓
Practice
  ↓
Solve
  ↓
Evaluate
  ↓
Analyze
  ↓
Identify Weak Areas
  ↓
Revise
  ↓
Improve
  ↓
Prepare for Exams
```

---

# 🧠 Long-Term Agentic Vision

The long-term objective is to evolve VidyānVaya AI into a more intelligent academic agent.

The planned architecture is:

```text
Student Query
      ↓
AI Agent / Query Router
      │
      ├── Topic Explanation
      │
      ├── Question Solving
      │
      ├── Question Bank
      │
      ├── Practice Test Generation
      │
      ├── Answer Evaluation
      │
      ├── Performance Analysis
      │
      └── Study Recommendation
```

The current development approach prioritizes a reliable document-processing and RAG foundation before progressively expanding the agentic layer.

---

# 🧪 Evaluation Strategy

The system is being evaluated using academic materials from different subjects and document types.

Current validation has covered:

- PDF processing
- DOCX processing
- PPTX processing
- Scanned PDF OCR
- Question-paper extraction
- Question Bank generation
- Semantic retrieval
- Document-specific retrieval
- AI Question Solver
- Practice-test generation
- AI answer evaluation
- Performance analysis
- Weak-area detection
- Personalized recommendations
- Multi-LLM provider fallback

Future evaluation will focus on:

- Multi-document retrieval quality
- Relevance of retrieved content
- Accuracy of explanations
- Quality of question solutions
- Quality of generated practice questions
- Subject adaptability
- Personalization effectiveness
- User experience
- Application reliability
- End-to-end workflow stability

---

# 📌 Current Project Status

## Development Status: Week 8 — Deployment & Finalization ✅

VidyānVaya AI has completed the planned 8-week development cycle.

### Completed Through Week 8

- Project foundation
- Streamlit application
- PDF processing
- DOCX processing
- PPTX processing
- OCR support for scanned PDFs
- Text chunking
- Sentence Transformer embeddings
- ChromaDB vector storage
- Semantic retrieval
- Document-specific retrieval
- Subject Guide / Academic Q&A
- Question Paper processing
- AI Question extraction
- Question Bank
- Question selection
- AI Question Solver
- Exam-oriented solutions
- Academic source display
- Gemini integration
- Multi-LLM provider layer
- Provider fallback mechanism
- Ollama local LLM support
- AI-generated practice tests
- Topic selection
- Difficulty selection
- Student answer submission
- AI answer evaluation
- Score generation
- Feedback generation
- Ideal-answer generation
- Performance tracking
- Overall performance analysis
- Topic-wise performance analysis
- Weak-area detection
- Strong-area detection
- Personalized study recommendations
- Unified modern dashboard
- UI/UX refinement
- End-to-end testing
- Deployment
- Final documentation
- Demo recording
- Final project submission

### Deployment Status

The application is deployed and publicly accessible:

https://vidyanvaya-ai.streamlit.app/

### Submission Status


---

# 📄 Project Information

| Field | Details |
|---|---|
| Project Name | VidyānVaya AI |
| Official Project | Subject Guide & Question Bank Assistant AI Agent |
| Development Approach | RAG Foundation → Advanced Agentic Capabilities |
| Duration | 8 Weeks |
| Current Stage | Week 8 — Deployment & Finalization |
| Completed Through | Week 8 |
| Domain | Educational Technology / Academic Learning |
| Architecture | Multi-Source RAG + Multi-LLM + Agentic Layer |
| Primary Interface | Streamlit |
| Repository | GitHub |

---

# 🔮 Future Scope

Future development may include:

- Advanced agentic workflows
- Intelligent query routing
- Adaptive learning
- Personalized study paths
- Advanced knowledge graphs
- Advanced learning analytics
- Multi-language academic support
- Mobile application
- LMS integration
- Personalized tutoring
- Scalable cloud architecture
- Advanced progress tracking
- Long-term student learning profiles

---

# 👨‍💻 Developer

**Suhas Subramani**

Computer Science & Engineering — Data Science

GitHub:

https://github.com/Suhas2811/vidyanvaya-ai

---

# ⭐ Project

If you find VidyānVaya AI useful or interesting, consider giving the repository a ⭐.

**VidyānVaya AI — Learn from your materials. Solve with AI. Improve with personalized learning.**
````

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

The system will process and organize these materials and use a **Multi-Source Retrieval-Augmented Generation (RAG)** approach to provide relevant, source-grounded academic assistance.

The system is designed to be **subject-agnostic**. Instead of being built specifically for one subject such as Computer Science or Mathematics, EduNexa AI will adapt to the subject and content provided by each student.

---

## 🎯 Problem Statement

Students often have their learning materials distributed across different sources such as textbooks, lecture notes, laboratory manuals, assignments, and previous-year question papers.

Finding relevant information, understanding topics, solving questions, identifying weak areas, and planning exam preparation can therefore become difficult and time-consuming.

VidyānVaya AI aims to bring these materials together into one intelligent academic learning environment.

---

## 💡 Proposed Solution

VidyānVaya AI will provide a unified academic assistant that can:

1. Understand and process multiple academic document formats.
2. Organize information from different sources.
3. Retrieve relevant information from uploaded materials.
4. Explain academic topics using multiple sources.
5. Solve questions using relevant study material.
6. Generate topic-wise practice questions.
7. Support exam preparation workflows.
8. Identify weak areas based on student performance.
9. Provide personalized study recommendations.
10. Track learning progress.

The system will initially follow the **Track A foundation** described in the project guide and progressively incorporate selected advanced capabilities inspired by **Track B**, depending on project progress and feasibility.

---

## 🌐 Subject-Agnostic Approach

A major design principle of VidyānVaya AI is **subject independence**.

The system will not be hard-coded for a particular academic subject.

Instead, students will provide their own academic materials, and the system will build its understanding from those materials.

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

The same application should be able to work with these different academic contexts without requiring subject-specific code changes.

### Core principle

```text
Student
   ↓
Upload Academic Materials
   ↓
Document Processing
   ↓
Content & Topic Understanding
   ↓
Multi-Source RAG
   ↓
Academic AI Agent
   ↓
Explain / Solve / Practice / Assess / Recommend
```

---

## 🚀 Planned Features

### 1. Multi-Document Upload

Support for academic materials in multiple formats, including:

* PDF
* DOCX
* PPTX

Additional document-processing capabilities may be added later.

### 2. Multi-Source RAG

The system will retrieve relevant information from multiple uploaded sources and use that context to generate grounded responses.

### 3. Subject Guide

Students will be able to ask questions such as:

> "Explain this topic with examples."

The system will provide structured explanations using relevant academic materials.

### 4. Question Solver

Students will be able to upload or ask questions and receive step-by-step solutions based on the available study materials.

### 5. Question Bank & Practice

The system will provide topic-wise practice questions based on the student's academic content.

Planned question types may include:

* Multiple-choice questions
* Short-answer questions
* Descriptive questions
* Topic-based practice

### 6. Exam Preparation Assistant

The system will support exam-oriented learning workflows such as:

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

### 7. Weak-Area Identification

The system will analyze question-practice performance to identify topics where the student may need additional practice.

### 8. Personalized Recommendations

Based on the student's progress, the system will recommend:

* Topics to revise
* Relevant study material
* Questions to practice
* Suggested learning sequence

### 9. Progress Tracking

The system will maintain learning-related information such as:

* Topics attempted
* Questions attempted
* Performance
* Weak areas
* Learning progress

### 10. Agentic Assistance

An agentic layer will eventually determine the student's intent and select the appropriate academic capability, such as:

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

---

# 🏗️ Planned System Architecture

```text
                         STUDENT
                            │
                            ▼
                   ┌─────────────────┐
                   │   Streamlit UI  │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ AI Agent /      │
                   │ Query Router    │
                   └────────┬────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
      Subject Guide   Question Solver   Exam Assistant
             │              │              │
             └──────────────┼──────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │   RAG Engine    │
                   └────────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
            PDF           DOCX          PPTX
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                   Text Processing
                            │
                            ▼
                       Chunking
                            │
                            ▼
                       Embeddings
                            │
                            ▼
                    Vector Database
                            │
                            ▼
                          LLM
                            │
                            ▼
                  Grounded AI Response
```

The architecture will evolve as advanced features are introduced.

---

# 🛠️ Technology Stack

| Component             | Planned Technology       |
| --------------------- | ------------------------ |
| Programming Language  | Python                   |
| AI / Agent Framework  | LangChain                |
| User Interface        | Streamlit                |
| PDF Processing        | PyPDF2 / pdfplumber      |
| DOCX Processing       | python-docx              |
| PPTX Processing       | python-pptx              |
| Embeddings            | Suitable embedding model |
| Initial Vector Search | FAISS                    |
| Application Database  | SQLite                   |
| Large Language Model  | Google Gemini            |
| Version Control       | Git + GitHub             |
| Deployment            | Streamlit Cloud          |

The technology stack may evolve during development if a different tool provides better performance, reliability, or scalability.

---

# 📅 8-Week Development Roadmap

## Week 1 — Foundation & Project Setup

### Objectives

* Finalize project architecture.
* Set up the development environment.
* Configure the initial Python, LangChain and Streamlit environment.
* Establish the basic application structure.
* Begin the document-processing foundation.
* Define the data flow for the subject-agnostic system.

### Expected Outcome

A clear technical foundation and initial working application structure.

---

## Week 2 — Multi-Source RAG

### Objectives

* Implement PDF, DOCX and PPTX processing.
* Extract and clean academic content.
* Split documents into meaningful chunks.
* Generate embeddings.
* Create the initial vector-search system.
* Implement basic multi-source retrieval.

### Expected Outcome

The system can retrieve relevant information from multiple uploaded academic documents.

---

## Week 3 — Subject Guide

### Objectives

* Implement topic-based retrieval.
* Generate comprehensive topic explanations.
* Combine information from multiple sources.
* Add source-aware responses.
* Organize content by subject and topic.

### Expected Outcome

Students can ask questions about topics and receive explanations grounded in their uploaded materials.

---

## Week 4 — Question Bank & Question Solver

### Objectives

* Process previous-year question papers.
* Retrieve relevant questions.
* Implement question-solving functionality.
* Generate step-by-step solutions.
* Connect questions with relevant study material.
* Add topic-wise practice question generation.

### Expected Outcome

The system can explain topics and solve academic questions using the student's materials.

---

## Week 5 — Exam Preparation Assistant

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

The project will initially use the **Track A foundation** to ensure that the core academic RAG functionality is reliable and achievable within the project timeline.

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

# 🧪 Planned Evaluation

The final system will be tested using academic materials from multiple subject areas.

The evaluation will focus on:

* Multi-document retrieval quality
* Relevance of retrieved content
* Accuracy of explanations
* Quality of question solutions
* Question-generation quality
* Subject adaptability
* Personalization effectiveness
* User experience
* Application reliability

The system will ideally be demonstrated using multiple different academic subjects to validate its subject-agnostic design.

---

# 📌 Expected Final Outcome

The final goal is to develop ** VidyānVaya AI **, a subject-agnostic Agentic AI academic learning assistant that can transform a student's own academic materials into an interactive learning environment.

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

The project will prioritize reliable multi-source academic retrieval and grounded responses first, followed by personalization and advanced agentic capabilities.

---

# 🔮 Future Scope

Future development may include:

* Support for additional document formats
* OCR for scanned academic materials
* Advanced knowledge graphs
* More sophisticated adaptive learning
* Mobile application
* LMS integration
* Advanced learning analytics
* Multi-language academic support
* More advanced personalized tutoring
* Scalable cloud architecture

---

# 👨‍💻 Development Status

**Current Status:** Pre-development / Project Planning

### Completed

* Project selected
* Project scope defined
* Subject-agnostic approach defined
* Initial technology stack selected
* System architecture planned
* 8-week development roadmap prepared
* GitHub repository created

### Upcoming

Development will begin with the foundation and document-processing phase.

---

## 📄 Project Information

**Project:** VidyānVaya AI
**Official Project:** Subject Guide & Question Bank Assistant AI Agent
**Development Approach:** Track A foundation → Selected advanced capabilities
**Duration:** 8 Weeks
**Domain:** Educational Technology / Academic Learning
**Architecture:** Multi-Source RAG + Agentic AI
**Primary Interface:** Streamlit

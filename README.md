# AI-Driven Virtual Interview and Skill Assessment Platform

> **Final-Year Project Synopsis & Implementation**  
> *A comprehensive, automated, multi-round virtual recruitment preparation platform developed in Python.*

---

## 📌 1. Project Overview

The **AI-Driven Virtual Interview and Skill Assessment Platform** is an intelligent web-based application designed to help students and job seekers prepare for IT-sector recruitment processes through an interactive and automated assessment environment. 

The platform simulates a real-world multi-stage placement process:
1. **Round 1 – Aptitude Assessment:** Evaluates Quantitative Ability, Logical Reasoning, and Verbal Ability through an automatically scored objective test with step-by-step explanations.
2. **Round 2 – AI-Powered HR Interview:** Assesses communication, confidence, STAR (Situation, Task, Action, Result) methodology, and behavioral responses with interactive voice synthesis (TTS) and speech-to-text dictation (STT).
3. **Round 3 – AI-Driven Technical Interview:** Domain-specific conceptual and architectural evaluation tailored to the candidate's chosen domain (Python & Backend, Full Stack, Data Science/AI, Databases & SQL, Java & OOP, Cloud/DevOps).
4. **Optional Technical Component – Live Coding Sandbox:** Algorithmic problem-solving environment executing Python code against test suites in an isolated execution sandbox.
5. **Holistic Analytics & Performance Report:** Generates round-wise scorecards, Plotly radar competency diagrams, identified strengths/weaknesses, a 4-week placement roadmap, and downloadable printable evaluation reports.

---

## 🎯 2. Objectives

- **Simulate Real Placement Rounds:** Replicate actual multi-tier campus and off-campus recruitment pipelines.
- **Interactive AI Interviewer:** Provide interactive conversational dialogue capable of asking contextual questions and following up on candidate responses.
- **Automated Objective & Subjective Evaluation:** Instant scoring for quantitative/logical aptitude and NLP-driven semantic assessment for descriptive responses.
- **Voice-Enabled Experience:** Utilize Text-to-Speech (TTS) for natural question audio delivery and Speech-to-Text (STT) for microphone dictation.
- **Actionable Feedback & Analytics:** Deliver multidimensional competency radar charts and a structured preparation roadmap.

---

## 🛠️ 3. Technologies Used

| Category | Technology |
| :--- | :--- |
| **Programming Language** | Python 3.x |
| **Frontend / Web Framework** | Streamlit |
| **Backend & Logic** | Python |
| **Database** | SQLite3 (`interview_platform.db`) |
| **AI / NLP Engine** | Hybrid Engine (Built-in Heuristic NLP + Google Gemini API support) |
| **Data Processing** | Pandas |
| **Visual Analytics** | Plotly (Radar Charts, Performance Comparisons) |
| **Speech-to-Text (STT)** | HTML5 Web Speech Recognition API |
| **Text-to-Speech (TTS)** | HTML5 Web Speech Synthesis API |
| **Execution Environment** | Isolated In-Memory Python Sandbox |

---

## 🏗️ 4. System Architecture

```text
                                  +---------------------------------------+
                                  |     Candidate / Job Seeker            |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |    Streamlit Responsive Web UI        |
                                  | (Dashboard, Assessment, Audio Widget) |
                                  +-------------------+-------------------+
                                                      |
        +---------------------------------------------+---------------------------------------------+
        |                                             |                                             |
        v                                             v                                             v
+---------------+                             +---------------+                             +---------------+
|    Round 1    |                             |    Round 2    |                             |    Round 3    |
|   Aptitude    |                             |  AI HR Round  |                             |  AI Technical |
|  Assessment   |                             | (STAR/Speech) |                             | (Domain/Code) |
+-------+-------+                             +-------+-------+                             +-------+-------+
        |                                             |                                             |
        +---------------------------------------------+---------------------------------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |     AI Evaluation & NLP Engine        |
                                  | - Keyword & Concept Density           |
                                  | - STAR Structure Detection            |
                                  | - Contextual Follow-up Generation     |
                                  | - Google Gemini REST Integration      |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |            SQLite Database            |
                                  | (Users, Questions, Transcripts, Logs) |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   Final Performance Analytics Report  |
                                  | - Plotly Radar & Cutoff Charts        |
                                  | - Strengths & Improvements            |
                                  | - 4-Week Placement Roadmap            |
                                  | - Exportable/Printable HTML Document  |
                                  +---------------------------------------+
```

---

## 📂 5. Project File Structure

```text
antigravity/
│
├── app.py                  # Main Streamlit web application & multi-page navigation
├── database.py             # SQLite database schema, seeding, queries, and session management
├── ai_engine.py            # Hybrid AI/NLP evaluation engine, question banks, and report logic
├── speech_helper.py        # Web Speech API integrations (TTS audio player & STT microphone dictation)
├── coding_runner.py        # Python code execution sandbox and test case validation runner
├── report_generator.py     # Plotly interactive charts and exportable printable HTML generator
├── requirements.txt        # Python package dependencies
├── run.bat                 # One-click Windows application launcher
└── README.md               # Project documentation & synopsis alignment
```

---

## 🚀 6. Getting Started & Execution

### Prerequisites
Make sure Python 3.10+ is installed on your system.

### Step 1: Install Dependencies
Open a command prompt in the project root directory and run:
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database (Optional)
The database automatically initializes upon app start, but can be verified with:
```bash
python database.py
```

### Step 3: Launch the Application
Run via Streamlit:
```bash
streamlit run app.py
```
*(Or simply double-click `run.bat` on Windows!)*

Once launched, the web application will open in your default browser at `http://localhost:8501`.

---

## 🔑 7. Demo Credentials

The database comes pre-seeded with a sample candidate account:
- **Username:** `candidate`
- **Password:** `demo123`

You can also use the **New Registration** tab to create a personalized profile with your target role and technical skills.

---

## 📚 8. References (From Project Synopsis)

1. **Jurafsky, D. & Martin, J. H. (2023).** *Speech and Language Processing.* Pearson / online draft.
2. **Russell, S. & Norvig, P. (2021).** *Artificial Intelligence: A Modern Approach.* Pearson.
3. **Streamlit Documentation.** Streamlit Inc. (`https://docs.streamlit.io`)
4. **Python Software Foundation.** Python Documentation. (`https://docs.python.org`)
5. **SQLite Documentation.** SQLite.org. (`https://www.sqlite.org`)
6. **Pandas Documentation.** NumFOCUS / pandas development team. (`https://pandas.pydata.org`)

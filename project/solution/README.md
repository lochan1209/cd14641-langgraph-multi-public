# Agentic AI Knowledge Assistant for Uda‑Hub
Project Overview
This project implements a modular Agentic AI system for the Uda‑Hub application using a custom LangGraph workflow.
The system enables intelligent question answering, information retrieval, and reasoning over customer and article data provided by Uda‑Hub’s first customer, Cultpass.
Key capabilities include:

Intent‑driven multi‑agent orchestration
Retrieval‑Augmented Generation (RAG)
Short‑term (session) and long‑term (semantic) memory
Tool‑based database abstraction
Fully customizable workflow graph (no prebuilt workflows)

All components are implemented under the solution/ directory as required.

# Agentic System Design
The system is designed around a multi‑agent architecture, where each agent has a single responsibility.
Agents

Intent Agent -> Classifies the user’s intent
Retrieval Agent -> Retrieves relevant data using RAG
Analysis Agent -> Reasons over retrieved knowledge
Action Agent -> Generates structured or final answers
Memory Agent -> Maintains short‑term and long‑term memory


# Workflow (Custom LangGraph)
User Input
   ↓
Intent Agent
   ↓
Retrieval Agent  ←→ Retrieval Tools
   ↓
Analysis Agent
   ↓
Action Agent
   ↓
Memory Agent
   ↓
END


# Note:
The workflow is implemented from scratch in agentic/workflow.py and does not use any prebuilt graphs.


# Project Structure
solution/
├── agentic/
│   ├── agents/          # All agent implementations
│   ├── tools/           # Database & action tools
│   ├── design/          # Architecture docs & diagrams
│   └── workflow.py      # Custom LangGraph workflow
├── data/
│   ├── core/
│   ├── external/
│   └── models/
├── tests/               # Automated tests
├── utils.py             # Chat interface & helpers
├── 03_agentic_app.py    # Main runnable application
├── requirements.txt
└── README.md


## Getting Started
# Prerequisites

Python 3.10+
OpenAI API Key (via environment variable)
Jupyter Notebook (for DB setup steps)

# Dependencies
All dependencies are listed in requirements.txt.
Core libraries include:
langgraph
langchain
langchain-openai
openai
pandas
numpy
sqlite3
python-dotenv

# Installation

Clone the repository

git clone <repository_url>cd solutionShow more lines

Create and activate a virtual environment

python -m venv venvsource venv/bin/activate   # macOS/Linuxvenv\Scripts\activate      # WindowsShow more lines

Install dependencies

pip install -r requirements.txtShow more lines

Set environment variable (do not commit .env)

Shellexport OPENAI_API_KEY="your_api_key_here"Show more lines

# Data Setup
Run the provided notebooks before executing the agentic app:

# External database

Plain Text01_external_db_setup.ipynb

# Core Uda‑Hub database

Plain Text02_core_db_setup.ipynb
Data Expansion Requirement
The file cultpass_articles.jsonl was expanded from 4 to 14+ articles, covering diverse topics such as:

Fitness programs
Nutrition
Mental health
Subscription plans
Pricing & refunds
App usage guidance

No large .db files are submitted.

# Running the Application
Run the agentic system using:
python 03_agentic_app.py
This launches an interactive chat interface defined in utils.py.
Optional enhancements to the chat interface are documented inside the file.

# Memory Strategy

Short‑term memory: Managed using thread_id (session‑based)
Long‑term memory: Implemented via semantic retrieval over stored knowledge

This allows the assistant to:

Maintain conversational context
Recall previously referenced entities
Improve response relevance over time


## Testing
Automated tests are provided under the tests/ directory.
Run all tests
Shellpytest tests/Show more lines
Test Coverage Includes

-> Agent behavior validation
-> Tool reliability
-> Workflow routing logic
-> Memory persistence
-> Edge cases (missing data, ambiguous queries)


## Built With

LangGraph – Custom agent workflows
LangChain – Agent & tool abstractions
OpenAI GPT Models
SQLite – Lightweight local storage
Python 3.10

## Notes & Restrictions

 No references to starter/ at runtime
 No .env file submitted
 No large database files committed
 All artifacts contained in solution
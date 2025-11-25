# InfinitePay Agent Swarm 

A containerized Multi-Agent System designed to act as an intelligent Customer Support Swarm. Built with **CrewAI**, **FastAPI**, and **Supabase**, this solution implements a **Sovereign Router Architecture** to efficiently handle user inquiries ranging from general product questions to sensitive account troubleshooting.

## Architecture & Design

### The "Multi-Agentic System" Pattern
This solution avoids a non-deterministic mesh network. Instead, it utilizes a **Hub & Spoke** architecture (Nested Crews) where a central Router acts as the sole entry point, delegating tasks to specialized sub-crews via tools.

**System Topology:**

```
USER QUERY
│
▼
[Streamlit Frontend]
│
▼
[FastAPI Backend]
│
▼
[ROUTER AGENT] (Agent 1)
│
├── Intent: Information? ───────────────────> [DelegateToKnowledge Tool]
│                                                   │
│                                           (Spins up Knowledge Crew)
│                                                   │
│                                           [KNOWLEDGE AGENT] (Agent 2)
│                                                   │
│                                   ┌───────────────┴───────────────┐
│                                   │                               │
│                           [InfinitePay RAG Tool]          [Web Search Tool]
│                                   │                               │
│                           (Supabase Vector Store)           (Serper Dev)
│
└── Intent: Support? ───────────────────────> [DelegateToSupport Tool]
                                                    │
                                            (Spins up Support Crew)
                                                    │
                                            [SUPPORT AGENT] (Agent 3)
                                                    │
                                            ┌───────┴───────┐
                                            │               │
                                  [TransactionStatus]   [AccountDetails]
                                            │               │
                                      (Supabase SQL)  (Supabase SQL)
```
### Agents Overview

* **Router Agent:** The flow manager. It strictly performs intent classification and delegation. It does not access data directly.
* **Knowledge Agent:** The product expert. Configured to answer in Markdown format using RAG (Retrieval Augmented Generation) for official documentation (vetorized) or Web Search for general facts.
* **Support Agent:** The technical support specialist. It has read-only access to user data (SQL) to diagnose transaction failures and account status, translating technical errors into user-friendly language.

## RAG Pipeline Implementation

The Knowledge Agent utilizes a RAG pipeline grounded in InfinitePay's official documentation.

1.  **Ingestion:** Content was scraped from infinitepay.io using an n8n workflow.
2.  **Embedding:** Text chunks were converted to vectors using `text-embedding-004`.
3.  **Storage:** Vectors and metadata (source URLs) are stored in Supabase (PostgreSQL with `pgvector`).
4.  **Retrieval:** The `InfinitePayKnowledgeTool` performs a cosine similarity search (`match_documents` RPC) to retrieve context before generation.

## Project Structure
```
CW_CODING_CHALLENGE/
├── backend/
│   ├── src/
│   │   ├── agents.py       # Definition of Router, Knowledge, and Support agents
│   │   ├── main.py         # FastAPI Entrypoint and Crew orchestration
│   │   ├── tasks.py        # Definition of Tasks and Decision Rules
│   │   └── tools.py        # Custom Tools (RAG, SQL, Web, Delegation)
│   ├── Dockerfile          # Backend container configuration
│   └── requirements.txt    # Python dependencies for backend
├── frontend/
│   ├── app.py              # Streamlit User Interface
│   ├── Dockerfile          # Frontend container configuration
│   └── requirements.txt    # Python dependencies for frontend
├── .dockerignore
├── .env                    # Environment variables (API Keys)
├── .gitignore
├── docker-compose.yml      # Orchestration of services
├── pyproject.toml
└── README.md
```
## Setup & Execution

### Prerequisites
* Docker & Docker Compose installed.
* API Keys for **Google Gemini**, **Supabase**, and **Serper.dev**.

### Configuration
1.  Clone the repository.
2.  Create a `.env` file in the root directory:

```
GOOGLE_API_KEY=your_gemini_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SERPER_API_KEY=your_serper_key
API_URL=http://backend:8000/api/chat
```
____

## Running with Docker
The project includes a docker-compose.yml that builds both the backend and frontend services.
```
docker-compose up --build
```

Access the services:
- Frontend (Chatbot): http://localhost:8501
- Backend API (Swagger): http://localhost:8000/docs

## Testing Strategy

The solution includes a Streamlit frontend specifically designed for integration testing, allowing the simulation of different user contexts via the sidebar.

### Test Cases:

1.  **RAG Retrieval:**
    * **Input:** "What are the fees for Maquininha Smart?"
    * **Validation:** PREENCHER

2.  **SQL Data Access:**
    * **Input:** "Why did my transaction fail?" (Set User ID: `client789`)
    * **Validation:** PREENCHER

3.  **External Search:**
    * **Input:** "Who won the last Palmeiras match?"
    * **Validation:** PREENCHER

4.  **Language Adaptation:**
    * **Input:** "Minha transação falhou"
    * **Validation:** PREENCHER

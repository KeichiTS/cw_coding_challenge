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

## Testing Strategy

The solution includes a Streamlit frontend specifically designed for integration testing. Below are the verified outputs for the core requirements.

### Test Cases:

#### 1. RAG Retrieval (Knowledge Agent)
* **Input:** `"What are the fees of the Maquininha Smart?"`
* **Validation:** The agent must retrieve the data from the Vector Store and format it using Markdown tables.
    ```text
    The Maquininha Smart has a purchase cost and various transaction fees that depend on your monthly sales volume.

    ### Transaction Fees (Maquininha & InfiniteTap)
    | Sales Volume (Monthly) | Pix | Debit | Credit (1x) | Credit (12x) |
    | :--- | :--- | :--- | :--- | :--- |
    | Above R$ 80,000 | GRÁTIS | 0.75% | 2.69% | 8.99% |
    | Above R$ 40,000 | GRÁTIS | 0.79% | 2.79% | 9.56% |
    | Above R$ 20,000 | GRÁTIS | 0.85% | 2.89% | 10.12% |
    | Up to R$ 20,000 | GRÁTIS | 1.37% | 3.15% | 12.40% |

    Source: [Confira todas as taxas da InfinitePay](https://www.infinitepay.io/taxas)
    ```

#### 2. SQL Data Access (Support Agent)
* **Input:** `"Why did my transaction fail?"` (User ID: `client789`)
* **Validation:** The agent must query the SQL database, identify the specific failure reason, and explain it empathetically without exposing raw JSON code.
    ```text
    Hello! I checked your transaction history to understand what happened.

    The transaction of R$ 1,200.00 was not completed because, at that moment, there were insufficient funds in your account.

    I recommend checking your available balance before trying again. If you need any help topping up your account, I'm here to help!
    ```

#### 3. External Search (Web Tool)
* **Input:** `"Quais as principais notícias de São Paulo hoje?"`
* **Validation:** The agent must recognize that this is not an InfinitePay product question, switch to the Web Search tool, and provide real-time news with sources.
    ```text
    As principais notícias de São Paulo hoje incluem:

    ### Violência e Criminalidade
    * A polícia investiga a identidade dos homens vistos saindo da casa de um cabeleireiro encontrado morto. (Fonte: g1 São Paulo)
    * Um homem foi preso após manter os filhos reféns em Campinas. (Fonte: CNN Brasil)

    ### Previsão do Tempo
    * São Paulo pode ter chuva intensa de até 100mm e ventos de 50 a 100 km/h. (Fonte: CNN Brasil)
    * A previsão para terça-feira (25) indica um dia amanhecendo chuvoso. (Fonte: Agência SP)

    Fontes:
    - [g1 São Paulo](https://g1.globo.com/sp/sao-paulo/)
    - [CNN Brasil](https://www.cnnbrasil.com.br/)
    ```

#### 4. Language Adaptation (Polyglot)
* **Input:** `"Quais foram os valores da minha ultimas transações?"`
* **Validation:** The agent must detect the Portuguese language and return the SQL data report completely in Portuguese.
    ```text
    Olá! Entendo que você gostaria de saber sobre suas últimas transações. Fiz uma verificação:

    1. R$ 150,00 - Aprovada.
    2. R$ 1.200,00 - Não concluída (Saldo Insuficiente).
    3. R$ 50,00 - Falha (Bloqueio temporário de segurança).
    4. R$ 25,00 - Aprovada.

    Para resolver o bloqueio da transação de R$ 50,00, por favor, entre em contato com nossa equipe de segurança.
    ```


## System summary

This project implements an ecommerce retrieval-augmented generation (RAG)with:

- a FastAPI backend,
- a Streamlit chat UI,
- Qdrant for hybrid retrieval,
- OpenAI and Groq integrations,
- LangSmith tracing,
- Ragas-based evaluation.

The current pipeline answers product questions from an Amazon items collection stored in Qdrant. The API retrieves relevant product descriptions, builds a prompt from the retrieved items, and sends it to OpenAI for the final answer.assistant 

The runtime flow is:

1. the user asks a question in the Streamlit UI,
2. the UI posts the query to the API,
3. the API runs the retrieval and generation pipeline,
4. the pipeline embeds the query, retrieves relevant product records, builds a prompt, and generates a structured answer,
5. the API returns the answer plus supporting context,
6. the UI renders the answer and product suggestions.

## Repository layout

```text
.
├── apps/
│   ├── api/            # FastAPI backend and RAG pipeline
│   └── chatbot_ui/     # Streamlit frontend
├── notebooks/          # Dataset, retrieval, prompt, and evaluation notebooks
├── docker-compose.yml  # Local multi-service runtime
├── Makefile            # Common project commands
├── pyproject.toml      # Workspace configuration
├── env.example         # Environment variable template
└── Product-README.md   # Product-facing overview
```

## Backend

The API lives in `apps/api`.

### HTTP surface

The backend exposes:

- `POST /rag`

Request body:

- `query`: the user question

Response body:

- `answer`: generated answer text
- `used_context`: supporting product items with:
  - `image_url`
  - `price`
  - `description`

### Core modules

- `apps/api/src/api/app.py`
  - creates the FastAPI app,
  - enables permissive CORS,
  - mounts the API router.

- `apps/api/src/api/api/endpoints.py`
  - defines the `/rag` route,
  - calls the pipeline wrapper,
  - converts the pipeline output into response models.

- `apps/api/src/api/api/models.py`
  - defines request and response schemas with Pydantic.

- `apps/api/src/api/agents/retrieval_generation.py`
  - implements the RAG pipeline:
    - query embedding,
    - Qdrant retrieval,
    - context formatting,
    - prompt rendering,
    - structured answer generation.

- `apps/api/src/api/agents/agents.py`
  - contains a small helper for provider-based LLM calls.

- `apps/api/src/api/agents/utils/prompt_management.py`
  - loads prompt templates from YAML,
  - supports pulling prompts from LangSmith.

- `apps/api/src/api/core/config.py`
  - loads API credentials from environment variables.

## Retrieval and generation flow

The pipeline is centered on the `Amazon-items-collection-01-hybrid-search` Qdrant collection.

Retrieval uses:

- dense semantic search with OpenAI embeddings,
- sparse BM25-style search,
- rank fusion to combine retrieval signals.

Generation uses a structured model definition so the response contains both:

- the final answer,
- references to items used to support that answer.

The API then enriches those references with product metadata such as image and price before returning them to the UI.

## Frontend

The UI lives in `apps/chatbot_ui`.

### Core behavior

- keeps chat history in Streamlit session state,
- sends each user message to the backend API,
- renders the assistant response,
- shows supporting product suggestions in the sidebar.

### Key files

- `apps/chatbot_ui/src/chatbot_ui/app.py`
  - main Streamlit app,
  - chat interface,
  - API integration,
  - suggestions sidebar.

- `apps/chatbot_ui/src/chatbot_ui/core/config.py`
  - reads the backend API URL from environment variables.

## Evaluation

The repository includes retrieval and RAG evaluation tooling.

### Evaluation script

- `apps/api/evals/eval_retriever.py`

This uses:

- LangSmith evaluation,
- Ragas metrics for:
  - context precision,
  - context recall,
  - faithfulness,
  - response relevancy.

### Run evaluation

```bash
make run-evals-retriever
```

## Notebooks

The notebook track documents the project’s development and experimentation.

### Prerequisites

- `notebooks/prerequisites/01-llm-apis.ipynb`

### Week 1

- `01-explore-amazon-dataset.ipynb`
- `02-RAG-preprocessing-items.ipynb`
- `03-RAG-pipeline.ipynb`
- `04-Observability-foundations.ipynb`
- `05-RAG-Eval-Dataset.ipynb`
- `06-RAG-Evals.ipynb`

### Week 2

- `01-Structured-Outputs-intro.ipynb`
- `02-Structured-Outputs-RAG-Pipeline.ipynb`
- `03-Hybrid-Search.ipynb`
- `04-Reranking.ipynb`
- `05-Prompt-Management.ipynb`

The prompt template used by the API is also stored in the week 2 prompt folder.

## Requirements

- Python 3.12+
- Docker and Docker Compose
- OpenAI API key
- Groq API key
- Qdrant
- LangSmith credentials if tracing/evaluation is enabled

## Environment setup

Copy the example environment file:

```bash
cp env.example .env
```

Populate at least:

- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`

## Running locally

Start the full stack with:

```bash
make run-docker-compose
```

This launches:

- the FastAPI backend,
- the Streamlit UI,
- Qdrant.

### Service ports

- Streamlit UI: `http://localhost:8501`
- API: `http://localhost:8000`
- Qdrant: `http://localhost:6333`

## Useful commands

```bash
make run-docker-compose
make clean-notebook-outputs
make run-evals-retriever
```

## Notes

- The API expects a running Qdrant instance.
- Inside Docker, the API points to `http://qdrant:6333`.
- Inside Docker, the UI points to `http://api:8000`.



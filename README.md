# MiniRAG — Production-Style Retrieval-Augmented Generation System

MiniRAG is an end-to-end Retrieval-Augmented Generation (RAG) system built to explore how modern AI applications can move beyond simple LLM calls into a complete, asynchronous, containerized architecture.

The system allows users to upload documents, process and chunk their content, generate embeddings, store them in PostgreSQL with pgvector, retrieve relevant context using vector search, and generate grounded answers using locally hosted Ollama models.

The project also includes a web interface, asynchronous background processing with Celery, monitoring, persistent storage, and an Nginx reverse proxy.

---

## Features

- Document upload and processing
- Configurable text chunking and overlap
- Local embedding generation with Ollama
- PostgreSQL + pgvector vector storage
- Semantic vector search
- Retrieval-Augmented Generation (RAG)
- Local LLM inference with Ollama
- Asynchronous document processing
- Celery background workers
- RabbitMQ task broker
- Redis result backend
- Idempotent background task handling
- Project-based document collections
- Reset and rebuild knowledge indexes
- FastAPI REST API
- Interactive RAG web interface
- Retrieval trace inspection
- Dockerized multi-service architecture
- Nginx reverse proxy
- Prometheus metrics
- Grafana monitoring
- PostgreSQL exporter
- Node exporter
- Flower task monitoring

---

# Architecture

```text
                         ┌──────────────────────┐
                         │        User          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │        Nginx         │
                         │ Reverse Proxy + UI   │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   │                                 │
                   ▼                                 ▼
          ┌─────────────────┐               ┌─────────────────┐
          │    Frontend     │               │     FastAPI     │
          │ HTML / CSS / JS │               │    REST API     │
          └─────────────────┘               └────────┬────────┘
                                                    │
                           ┌────────────────────────┼─────────────────────┐
                           │                        │                     │
                           ▼                        ▼                     ▼
                  ┌────────────────┐       ┌────────────────┐   ┌────────────────┐
                  │   RabbitMQ     │       │ PostgreSQL +   │   │     Ollama     │
                  │  Task Broker   │       │    pgvector    │   │ LLM + Embedding│
                  └───────┬────────┘       └────────────────┘   └────────────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │ Celery Workers │
                  │ Process/Index  │
                  └───────┬────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │     Redis      │
                  │ Result Backend │
                  └────────────────┘


             ┌──────────────── Monitoring ────────────────┐
             │                                             │
             │ Prometheus → Grafana                        │
             │ PostgreSQL Exporter                         │
             │ Node Exporter                               │
             │ Flower                                      │
             └─────────────────────────────────────────────┘
```

---

# RAG Pipeline

The main document pipeline is:

```text
Upload Document
      │
      ▼
Extract Text
      │
      ▼
Chunk Document
      │
      ▼
Generate Embeddings
      │
      ▼
Store Chunks + Metadata
      │
      ▼
PostgreSQL / pgvector
```

When a user asks a question:

```text
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Vector Similarity Search
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Build RAG Prompt
      │
      ▼
Ollama LLM
      │
      ▼
Grounded Answer
```

---

# Tech Stack

## Backend

- Python
- FastAPI
- SQLAlchemy Async
- asyncpg
- Pydantic

## AI / RAG

- Ollama
- Local LLM
- EmbeddingGemma
- Retrieval-Augmented Generation
- Vector similarity search

## Data

- PostgreSQL
- pgvector
- Qdrant support / experimentation

## Async Processing

- Celery
- RabbitMQ
- Redis
- Flower

## Infrastructure

- Docker
- Docker Compose
- Nginx

## Monitoring

- Prometheus
- Grafana
- PostgreSQL Exporter
- Node Exporter

## Frontend

- HTML
- CSS
- JavaScript

---

# Project Structure

```text
mini_rag_system/
│
├── Docker/
│   ├── docker-compose.yml
│   ├── envs/
│   ├── nginx/
│   ├── prometheus/
│   ├── rabbitmq/
│   └── minirag/
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── src/
│   ├── controllers/
│   ├── models/
│   ├── routes/
│   ├── stores/
│   ├── tasks/
│   ├── utils/
│   ├── main.py
│   └── celeryapp.py
│
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

# Running MiniRAG Locally

The recommended way to run MiniRAG is with Docker Compose.

## 1. Prerequisites

Install:

- Git
- Docker
- Docker Compose

Verify the installation:

```bash
git --version
docker --version
docker compose version
```

---

## 2. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd mini_rag_system
```

---

## 3. Configure Environment Variables

The real environment files are intentionally excluded from Git.

Use the provided example configuration as a reference:

```text
.env.example
```

Create the required environment files inside:

```text
Docker/envs/
```

The current Docker setup expects configuration files for services such as:

```text
.env.app
.env.postgres
.env.postgres_exporter
.env.rabbitmq
.env.redis
.env.grafana
```

Do not commit real passwords, API keys, database credentials, or other secrets.

Make sure the application configuration includes the required PostgreSQL, Redis, RabbitMQ, Ollama, embedding model, generation model, and vector database settings.

---

## 4. Start the Docker Stack

Move to the Docker directory:

```bash
cd Docker
```

Build and start the services:

```bash
docker compose up -d --build
```

Check the containers:

```bash
docker compose ps
```

---

## 5. Download the Ollama Models

The Ollama container uses persistent storage, but models must be downloaded the first time the system is deployed.

Check available models:

```bash
docker compose exec ollama ollama list
```

Pull the embedding model:

```bash
docker compose exec ollama ollama pull embeddinggemma
```

Pull the generation model configured in your environment variables.

For example:

```bash
docker compose exec ollama ollama pull <GENERATION_MODEL>
```

Verify:

```bash
docker compose exec ollama ollama list
```

The model names must match the values configured in the application environment.

---

## 6. Verify the Services

Check that all containers are running:

```bash
docker compose ps
```

If something fails:

```bash
docker compose logs
```

For FastAPI:

```bash
docker compose logs fastapi
```

For Celery:

```bash
docker compose logs celery-worker
```

For Ollama:

```bash
docker compose logs ollama
```

---

## 7. Open the Application

Nginx is the public entry point.

Open:

```text
http://localhost
```

The frontend communicates with FastAPI through Nginx using relative `/api/...` routes.

The browser does not need direct access to port `8000`.

---

# Using the Application

A typical workflow is:

1. Select a Project ID.
2. Upload a supported document.
3. Configure chunk size and overlap.
4. Optionally enable index reset.
5. Start the processing pipeline.
6. Celery processes the document in the background.
7. Chunks are embedded and indexed in pgvector.
8. Refresh the project information.
9. Ask a question about the indexed document.
10. Inspect the retrieved context and generated response.

---

# Main API Endpoints

## Document Upload

```http
POST /api/v1/data/upload/{project_id}
```

Uploads a document to a project.

---

## Process Documents

```http
POST /api/v1/data/process/{project_id}
```

Queues document processing.

---

## Process and Index

```http
POST /api/v1/data/process_and_push/{project_id}
```

Runs the asynchronous processing and indexing workflow.

---

## Index Project

```http
POST /api/nlp/index/{project_id}
```

Indexes processed chunks into the vector database.

---

## Project / Collection Information

```http
GET /api/nlp/info/{project_id}
```

Returns information about the project's vector collection.

---

## Vector Search

```http
POST /api/nlp/index/search/{project_id}
```

Performs semantic retrieval against the indexed knowledge base.

---

## RAG Answer

```http
POST /api/nlp/index/answer/{project_id}
```

Retrieves relevant context and generates a grounded answer.

---

# Background Processing

Document processing and indexing are executed asynchronously using Celery.

The architecture uses:

```text
FastAPI
   │
   ▼
RabbitMQ
   │
   ▼
Celery Worker
   │
   ├── Document Processing
   └── Vector Indexing
   │
   ▼
Redis Result Backend
```

Dedicated Celery queues are used for different workloads:

```text
default
file_processing
indexing_data
```

---

# Vector Storage

MiniRAG currently uses PostgreSQL with the pgvector extension as its primary vector storage layer.

Vector collections are created dynamically according to the project and embedding configuration.

Each indexed chunk can contain:

- Chunk text
- Vector embedding
- Project ID
- Asset ID
- Chunk metadata
- Chunk order
- Unique identifiers

---

# Resetting an Index

The processing pipeline supports rebuilding project data using the `do_reset` option.

When enabled, existing project chunks are removed before the new document chunks are stored and indexed.

PostgreSQL primary key IDs may continue increasing after a reset. This is expected behavior because deleting rows does not reset the underlying sequence.

---

# Monitoring

The project includes a monitoring stack based on:

```text
FastAPI Metrics
      │
      ▼
Prometheus
      │
      ▼
Grafana
```

Additional metrics are collected using:

- PostgreSQL Exporter
- Node Exporter

Celery tasks can also be inspected using Flower.

Monitoring services are kept internal by default in the production-oriented Docker configuration rather than being exposed publicly.

---

# Production Architecture

For deployment, Nginx acts as the only public application entry point:

```text
Internet
   │
   ▼
Nginx :80 / :443
   │
   ├── /          → Frontend
   │
   └── /api/...   → FastAPI
                         │
                         ▼
                  Internal Docker Network
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
     Ollama          PostgreSQL       RabbitMQ
                       pgvector            │
                                          ▼
                                        Celery
```

Infrastructure services such as PostgreSQL, Redis, RabbitMQ, Ollama, Prometheus, Grafana, and Flower should not be exposed directly to the public internet.

---

# Deployment

The project is designed to run as a Docker Compose stack and can be deployed to a Linux server.

The current deployment target is:

**Amazon Lightsail / Ubuntu**

Typical deployment flow:

```bash
git clone <YOUR_REPOSITORY_URL>

cd mini_rag_system/Docker

# Configure production environment files

docker compose up -d --build

docker compose exec ollama ollama pull embeddinggemma
docker compose exec ollama ollama pull <GENERATION_MODEL>

docker compose ps
```

Then access the application through the server IP address or configured domain.

For production deployments, HTTPS should be configured and only required public ports should be allowed by the server firewall.

---

# Security Notes

- Secrets are stored in environment files and excluded from Git.
- Database credentials should never be committed.
- PostgreSQL is not publicly exposed.
- Redis is not publicly exposed.
- RabbitMQ is not publicly exposed.
- Ollama is not publicly exposed.
- FastAPI is accessed through Nginx.
- Monitoring services should remain private or be protected with authentication.
- HTTPS should be enabled for internet-facing deployments.

---

# Current Status

The core end-to-end RAG pipeline is operational:

```text
Document Upload        ✅
Document Processing    ✅
Chunking               ✅
Background Tasks       ✅
Embedding Generation   ✅
pgvector Indexing      ✅
Vector Search          ✅
RAG Answer Generation  ✅
Frontend Integration   ✅
Nginx Reverse Proxy    ✅
Docker Deployment      ✅
Monitoring Stack       ✅
```

---

# Roadmap

The next engineering phase focuses on improving retrieval quality and production RAG capabilities.

Planned areas include:

- Advanced document parsing
- Improved PDF and table extraction
- Chunking strategy experiments
- Embedding benchmarking
- Metadata filtering
- Hybrid dense + sparse retrieval
- Reranking
- Query routing
- Structured outputs
- RAG evaluation datasets
- Recall@K / MRR / nDCG evaluation
- RAG testing
- Security and prompt-injection defenses
- Arabic / multilingual RAG
- Streaming responses
- Conversation memory
- Agentic RAG experiments

---

# Why This Project?

MiniRAG was built as a hands-on engineering project to understand the complete lifecycle of a RAG application — not only retrieval and LLM prompting, but also:

- asynchronous processing
- vector database design
- container orchestration
- local model serving
- API architecture
- monitoring
- deployment
- retrieval evaluation
- production-oriented infrastructure

The goal is to continuously evolve the project from a working MiniRAG implementation into a more advanced production AI knowledge system.

---

# Author

**Youssef Rifat**

AI / Generative AI Engineer

Focused on:

`Python` · `FastAPI` · `RAG` · `LLMs` · `NLP` · `pgvector` · `Docker` · `Azure AI`

---

## License

See the `LICENSE` file for license information.
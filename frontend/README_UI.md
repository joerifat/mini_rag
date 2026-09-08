# MiniRAG Studio UI

A lightweight portfolio UI built for the existing FastAPI MiniRAG backend.

## What it uses from your backend

- `POST /api/v1/data/upload/{project_id}`
- `POST /api/v1/data/process_and_push/{project_id}`
- `GET /api/nlp/info/{project_id}`
- `POST /api/nlp/index/search/{project_id}`
- `POST /api/nlp/index/answer/{project_id}`

The UI reflects the actual stack in the repository: FastAPI, PostgreSQL/pgvector, Celery, Redis/RabbitMQ, Ollama, Prometheus/Grafana.

## Run

Start your backend as usual, then serve this folder:

```bash
cd frontend
python -m http.server 5500
```

Open `http://localhost:5500`.

Click the gear icon and set the FastAPI URL if it is not `http://localhost:8000`.

## CORS

Because this frontend is served from a different port, FastAPI needs CORS enabled. Add `CORSMiddleware` to `src/main.py` for your frontend origin (for local demo: `http://localhost:5500`).

## Portfolio flow

1. Choose a project ID.
2. Upload a document.
3. Configure chunk size / overlap.
4. Run the async processing + indexing pipeline.
5. Refresh index info until vectors appear.
6. Ask a question.
7. Show the Retrieval Trace to demonstrate that the answer is grounded in retrieved context.

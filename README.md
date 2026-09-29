# MEMORA: AI Customer Support Memory & Intelligence Platform

*Every customer has a history. Your support agent should remember it.*

MEMORA remembers every customer interaction, learns from previous resolutions, detects recurring problems, explains **why** it knows something, and intelligently connects AI support with human agents.

## Architecture

```
Customer message
  → Intent / entity / sentiment
  → Customer identification
  → Memory retrieval (similarity + importance + confidence + freshness)
  → Similar ticket retrieval
  → Knowledge base retrieval
  → Context ranking
  → Response generation (Anthropic / OpenAI-compatible / local fallback)
  → Confidence evaluation
  → Escalation analysis (explainable score)
  → Memory extraction + contradiction detection
  → Store
```

**Memory types:** `semantic`, `episodic`, `resolution_success`, `resolution_fail`, `preference`

Retrieval ranks by embedding similarity + importance + confidence (with gentle age decay). Short messages like "It happened again" are expanded with the customer's last ticket.

## Features

- **Customer 360** — profile, stats, memories, full timeline
- **Why I know this** — explainable memory selection with sources and confidence
- **Memory freshness** — Fresh / Recent / Aging / Possibly outdated (no silent deletes)
- **Contradiction detection** — environment/version conflicts with agent resolution actions
- **Explainable escalation** — scored signals (recurring, failed solutions, frustration, security, low confidence, open tickets)
- **Human agent takeover** — full context, internal notes, assign, reply, resolve
- **Product intelligence** — emerging multi-customer issues, trends, root-cause clusters
- **Analytics** — resolution mix, series charts, memory health
- **Knowledge base** — usage counts, helpfulness feedback, outdated flags
- **Global search** — customers, tickets, memories, KB
- **AI evaluation suite** — seeded test cases for retrieval and escalation honesty
- **Demo mode** — Ananya "It happened again" end-to-end flow

## Run

```bash
# Backend
cd backend
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
# API: http://localhost:8000  ·  Docs: http://localhost:8000/docs

# Frontend
cd frontend
npm install
npm run dev
# UI: http://localhost:5173
```

### Demo accounts

| Role     | Email                 | Password  |
|----------|-----------------------|-----------|
| Customer | ananya@example.com    | demo123   |
| Agent    | agent@memora.io       | agent123  |

### 60-second demo

1. Sign in as **Ananya**.
2. Send: `It happened again.`
3. MEMORA expands context from her last ticket, retrieves memories, shows **Why I know this**, similar tickets, confidence, and escalation analysis if warranted.
4. Sign in as the **agent** → Dashboard / Escalated queue → open the ticket → full handoff context, memories, notes, reply & resolve.
5. Product intelligence shows CloudSync v6.4.2 sync patterns across customers.

## Environment variables

| Variable | Default | Notes |
|----------|---------|-------|
| `MEMORA_SECRET` | `dev-only-change-me` | HMAC signing secret |
| `MEMORA_DB` | `memora.db` | SQLite path |
| `CORS` | `http://localhost:5173` | Comma-separated origins |
| `LLM_PROVIDER` | `local` | `anthropic` \| `openai` \| `local` |
| `LLM_MODEL` | — | Model name when using a provider |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | — | Provider keys |
| `OPENAI_BASE_URL` | OpenAI public API | Compatible gateways supported |
| `VITE_API` | `http://localhost:8000` | Frontend API base |

## API overview

- `POST /api/login`
- `POST /api/chat` — full pipeline + confidence + escalation + why-selected
- `GET/PATCH /api/tickets/{id}`, `POST .../outcome`, `.../agent-reply`, `.../notes`
- `GET /api/tickets` — agent list with filters
- `GET /api/customers`, `GET /api/customers/{cid}` — Customer 360
- `PATCH/DELETE /api/memories/{id}`, `POST /api/customers/{cid}/resolve-conflict`
- `GET /api/dashboard`, `/api/emerging`, `/api/product-intelligence`, `/api/analytics`
- `GET /api/search`, `/api/kb`, `POST /api/kb/{id}/feedback`, `/api/kb/outdated`
- `GET /api/eval/cases`, `POST /api/eval/run`
- `GET /api/health`

## Database

SQLite by default (demo-friendly). Tables: `users`, `customers`, `tickets`, `messages`, `memories`, `kb`, `notes`, `audit`.

Embeddings are hashing vectors (256-d). Swap `emb()` and the store for a real model + Postgres/pgvector when you need production retrieval quality.

## Testing

```bash
# Backend health after seed
curl -s http://localhost:8000/api/health

# Login + chat smoke (customer)
TOKEN=$(curl -s -X POST http://localhost:8000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"ananya@example.com","password":"demo123"}' | python -c "import sys,json; print(json.load(sys.stdin)['token'])")
curl -s -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"message":"It happened again."}' | python -m json.tool | head -40

# Evaluation suite (agent)
AGENT=$(curl -s -X POST http://localhost:8000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"agent@memora.io","password":"agent123"}' | python -c "import sys,json; print(json.load(sys.stdin)['token'])")
curl -s -X POST http://localhost:8000/api/eval/run -H "Authorization: Bearer $AGENT" | python -m json.tool
```

Frontend production build:

```bash
cd frontend && npm run build
```

## Known limitations

- Hashing embeddings (not a neural model); fine for demo ranking, not production semantic search.
- Rule-based memory extraction and contradiction heuristics.
- No multi-tenant isolation beyond role/cid checks.
- LLM optional — local fallback is deterministic over retrieved memories.
- SQLite single-file store; not concurrent-write hardened for high traffic.

## License

Demo / educational use.

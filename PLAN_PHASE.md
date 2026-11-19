# PLAN_PHASE – 13-Phase Build

Each phase is a checkpoint. All phases must pass `make test` (where applicable) before the next starts.
`make demo` must succeed at every phase that touches the ticket pipeline.

---

## Phase 1 — Runtime skeleton

**Goal:** Project structure, FastAPI app shell, fake LLM provider, base Pydantic models.

**Files:**
```
backend/app/__init__.py
backend/app/main.py              # FastAPI app, lifespan, /health/{live,ready}
backend/app/core/__init__.py
backend/app/core/config.py        # settings (pydantic BaseSettings, .env)
backend/app/core/logging.py       # JSON logger with request_id
backend/app/schemas/__init__.py
backend/app/schemas/base.py       # BaseResponse, BaseResponseItem
tests/conftest.py                 # fixtures: demo env vars, testclient, headers
tests/api/test_health.py
```

**PRD rows:** F1 (shell), NFR-1, NFR-2
**Tests:** health endpoints return 200, fake provider returns deterministic JSON
**Demo:** `make backend` starts, `curl http://localhost:8000/health/live` → 200
**Exit:** app starts without DB, passes all tests in <5 s

---

## Phase 2 — Persistence and demo data

**Goal:** SQLite database, Alembic migrations, seed data (customers, subscriptions, workspaces, sample KB articles).

**Files:**
```
backend/app/core/database.py          # async engine, sessionmaker
backend/app/models/__init__.py
backend/app/models/*.py               # SQLAlchemy ORM models for core tables
backend/app/seed.py                   # CLI: `python -m backend.app.seed`
backend/data/kb/                      # raw markdown articles (20-30 articles)
alembic.ini, alembic/                 # migration tooling
tests/api/test_seed.py                # seed + count rows
```

**PRD rows:** F4, F5 (raw articles)
**Tests:** each table has expected row count after seed
**Demo:** `make seed` populates DB, `sqlite3` shows correct counts
**Exit:** all ORM models load, Alembic shows no pending migrations

---

## Phase 3 — Identity and request guards

**Goal:** JWT auth, RBAC middleware, injection wrapper, audit log, security headers.

**Files:**
```
backend/app/core/security.py          # JWT create/verify, require_role
backend/app/routes/auth.py            # /auth/login, /auth/whoami
backend/app/models/user.py
backend/app/middleware/injection.py   # wrap_untrusted()
backend/app/middleware/audit.py       # audit_log on write endpoints
tests/api/test_auth.py                # login, token expiry, 401/403
tests/unit/test_injection.py          # prompt injection blocked
```

**PRD rows:** F12, F13
**Tests:** viewer 403 on write, agent can write, admin can reindex
**Demo:** `curl -X POST /auth/login` returns token, bearer works on /tickets
**Exit:** every route protected by `require_role`

---

## Phase 4 — Support API

**Goal:** Ticket CRUD, message log, customer lookup, dashboard summary.

**Files:**
```
backend/app/routes/tickets.py         # CRUD + /run + /workflow + /events
backend/app/routes/customers.py       # GET /customers, /customers/:id
backend/app/routes/dashboard.py       # /dashboard/summary
backend/app/schemas/tickets.py
backend/app/schemas/customers.py
tests/api/test_tickets.py             # CRUD, message append
tests/api/test_dashboard.py           # summary counts
```

**PRD rows:** F1, F4
**Tests:** create ticket → 201, list tickets → correct count, 404 on missing
**Demo:** `make demo TICKET=CD-1001` creates and lists tickets
**Exit:** full ticket lifecycle (create → update status) works end-to-end

---

## Phase 5 — Knowledge pipeline

**Goal:** Chunk, embed, index KB articles; semantic + keyword search with RRF and rerank.

**Files:**
```
backend/app/rag/chunker.py            # chunk_text(), max 512 tokens
backend/app/rag/embedder.py           # fake embeddings for test, real for prod
backend/app/rag/retriever.py          # search_kb(), RRF fusion, rerank
backend/app/routes/knowledge.py       # /knowledge/search, /knowledge/reindex
backend/app/models/knowledge.py
tests/rag/test_chunker.py
tests/rag/test_retriever.py           # expected article hit, cache, filters
```

**PRD rows:** F5, F6
**Tests:** search returns top article with score > 0.6; RRF fuses semantic + keyword
**Demo:** `make ingest` chunks 20+ articles, search returns correct KB hit
**Exit:** retriever works with both `memory` and real vector store backends

---

## Phase 6 — Tools and policy

**Goal:** Mock tool registry (billing lookup, refund, password reset, etc.), deterministic tool policy.

**Files:**
```
backend/app/tools/__init__.py         # ToolRegistry, tool schemas
backend/app/tools/billing.py          # mock refund, invoice lookup
backend/app/tools/account.py          # mock password reset, plan change
backend/app/tools/diagnostics.py      # mock service health check
backend/app/policy/tool_policy.py     # allow-list per role, money-gate
tests/unit/test_tool_policy.py        # deny money tools without approval
```

**PRD rows:** F7
**Tests:** policy blocks refund for viewer, allows for agent with approval flag
**Demo:** tool calls are recorded in `tool_calls` table
**Exit:** all tools mockable, no real HTTP calls

---

## Phase 7 — Rules and guardrails

**Goal:** Deterministic rules for severity, escalation triggers, money-gate, GDPR.

**Files:**
```
backend/app/rules/rule_severity.py    # classify severity from category + data
backend/app/rules/rule_escalation.py  # auto-escalate on risk signals
backend/app/rules/rule_guardrails.py  # what the LLM must never do
backend/app/guardrails.py             # pre/post-processing checks
tests/unit/test_rules.py              # severity, escalation triggers
tests/unit/test_guardrails.py         # injection containment, data leak prevention
```

**PRD rows:** F3, F13
**Tests:** critical severity on payment-failure + 3+ prior tickets
**Demo:** `make demo` triggers a rule-based auto-escalation
**Exit:** rules are pure functions, fully tested without LLM

---

## Phase 8 — Specialist agents

**Goal:** LangGraph agent nodes: CustomerAgent, KnowledgeAgent, Troubleshooter, Decider, ReplyAgent, SupervisorAgent.

**Files:**
```
backend/app/agents/supervisor.py      # understand, classify, assess_severity
backend/app/agents/customer.py        # load context
backend/app/agents/knowledge.py       # retrieve evidence, similar cases
backend/app/agents/troubleshooter.py  # call tools per policy
backend/app/agents/decider.py         # propose resolution
backend/app/agents/reply_agent.py     # draft customer reply
backend/app/schemas/agents.py
tests/agents/test_supervisor.py
tests/agents/test_customer.py
tests/agents/test_knowledge.py
tests/agents/test_troubleshooter.py
tests/agents/test_decider.py
tests/agents/test_reply_agent.py
```

**PRD rows:** F2, F4–F7
**Tests:** each agent returns correct Pydantic model with fake provider
**Demo:** `make demo TICKET=CD-1002` runs agents in sequence
**Exit:** all agents pass with `LLM_PROVIDER=fake`

---

## Phase 9 — Workflow graph and trace

**Goal:** Full LangGraph workflow connecting agents, WorkflowTracer, node-level events.

**Files:**
```
backend/app/workflow/graph.py         # compile() → compiled graph
backend/app/workflow/state.py         # TypedState definition
backend/app/workflow/trace.py         # WorkflowTracer
backend/app/workflow/reducers.py      # append-only reducers
backend/app/routes/workflow.py        # /tickets/:id/run, /workflow/:id
tests/workflow/test_graph.py          # shape, routing
tests/workflow/test_trace.py          # events logged correctly
tests/workflow/test_e2e.py           # low-risk ticket runs to completion
```

**PRD rows:** F14
**Tests:** graph has 10+ nodes, low-risk ticket completes without interrupt
**Demo:** `make demo` shows full workflow trace with events
**Exit:** every node in the pipeline fires in correct order

---

## Phase 10 — Approval and escalation

**Goal:** Interrupt on money/account actions, agent approve/reject, auto-escalation.

**Files:**
```
backend/app/routes/approvals.py       # /approvals, /approvals/:id/approve, /reject
backend/app/routes/escalations.py     # /escalations, /escalations/:id
backend/app/models/approval.py
backend/app/models/escalation.py
backend/app/workflow/interrupt.py     # interrupt_before(), resume()
tests/api/test_approvals.py           # refund pause → approve → complete
tests/api/test_escalations.py         # rejection → escalation
tests/workflow/test_pause_resume.py
```

**PRD rows:** F8, F9
**Tests:** refund pauses, viewer 403, agent approve/resume completes
**Demo:** `make demo TICKET=CD-1002` pauses at refund, agent approves
**Exit:** approval gate works end-to-end, audit log records all decisions

---

## Phase 11 — Memory

**Goal:** Post-resolution memory notes, PII sanitisation, memory retrieval for future tickets.

**Files:**
```
backend/app/agents/memory_agent.py    # summarise, sanitise, store
backend/app/routes/memory.py          # /memory (GET/POST)
backend/app/models/memory.py
tests/agents/test_memory_agent.py     # PII removed, summary stored
```

**PRD rows:** F10
**Tests:** card numbers and keys stripped from memory notes
**Demo:** `make demo` stores a memory note after resolution
**Exit:** memory notes retrievable for future tickets from same customer

---

## Phase 12 — Agent console (frontend)

**Goal:** Next.js app with login, dashboard, ticket detail (3-column), customer panel, knowledge search.

**Files:**
```
frontend/Next.config, tsconfig, package.json
frontend/src/app/layout.tsx, page.tsx
frontend/src/app/login/page.tsx
frontend/src/app/dashboard/page.tsx
frontend/src/app/tickets/[id]/page.tsx
frontend/src/app/customers/page.tsx
frontend/src/app/knowledge/page.tsx
frontend/src/app/escalations/page.tsx
frontend/src/app/audit/page.tsx
frontend/src/app/settings/page.tsx
frontend/src/lib/api.ts               # typed client, bearer token, 401 redirect
frontend/src/lib/types.ts             # mirrors API_CONTRACT.md
frontend/src/components/ui/           # shared components (StatusPill, EmptyState, etc.)
frontend/src/components/layout/nav.tsx
frontend/__tests__/test_components.ts
```

**PRD rows:** F11, NFR-4
**Tests:** StatusPill renders correctly, api.ts handles 401, usePolling works
**Demo:** `cd frontend && npm run dev` → login → dashboard → ticket detail
**Exit:** all pages render, nav reflects role, polling updates workflow steps

---

## Phase 13 — Evaluation and delivery

**Goal:** Eval thresholds, Docker Compose, Terraform scaffolds, CI workflows, API contract final.

**Files:**
```
backend/datasets/eval_cases.json      # 50+ cases with expected_category
tests/evaluation/test_eval.py         # threshold-gated eval
backend/Dockerfile, frontend/Dockerfile
docker-compose.yml
deployment/aws/main.tf, deployment/azure/main.tf, deployment/gcp/main.tf
.github/workflows/{test,security,docker-build,terraform-validate}.yml
docs/API_CONTRACT.md                  # final route/type contract
Makefile
.env.example
tests/deployment/test_compose.py
```

**PRD rows:** F14, NFR-5–7
**Tests:** classification ≥ 0.80, retrieval ≥ 0.75, escalation ≥ 0.90, citation ≥ 0.90
**Demo:** `docker compose up` → full stack running
**Exit:** all eval thresholds pass, Compose builds clean, Terraform validates

---

## Cross-cutting (every phase)

- `pyproject.toml` updated with new dependencies.
- `tests/conftest.py` updated with new fixtures.
- `Makefile` targets kept working.
- `docs/API_CONTRACT.md` updated when routes change.
- Honest status in `MEMORY.md` kept current.

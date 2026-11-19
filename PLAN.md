# PLAN – Requirement Catalog

Every row maps to one or more CLAUDE.md sections, tests, and a phase. This is the master checklist.

---

## Functional Requirements

| ID | Requirement | CLAUDE.md § | Phase |
|----|-------------|-------------|-------|
| F1 | Create ticket from email/chat/web/API | §5, §12 | 4 |
| F2 | Classify into one of 10 categories + one-line summary | §5, §6 | 8 |
| F3 | Severity low/medium/high/critical with reason | §5, §6 | 7 |
| F4 | Load customer, subscription, workspace, previous tickets, memory notes | §5, §6 | 4 |
| F5 | Cited evidence from KB (semantic + keyword, reranked) | §5, §7 | 5 |
| F6 | Similar previously resolved cases | §5, §6 | 5 |
| F7 | Troubleshoot – call allow-listed tools (mock) in a deterministic policy | §5, §6 | 6 |
| F8 | Decide resolution, detect money/account actions, request approval | §5, §6 | 10 |
| F9 | Execute resolution or escalate to human | §5, §6 | 10 |
| F10 | Persist memory notes (summary, action taken, lesson learned) | §5, §6 | 11 |
| F11 | Agent console: create/run/approve/reject/escalate tickets | §5, §10 | 12 |
| F12 | Role-based access (viewer/agent/admin) | §2, §9 | 3 |
| F13 | Security: injection containment, no raw prompt exposure, audit trail | §9 | 3 |
| F14 | Observability: JSON logs, WorkflowTracer, token usage, LangSmith optional | §16 | 9 |

## Non-Functional Requirements

| ID | Requirement | CLAUDE.md § | Phase |
|----|-------------|-------------|-------|
| NFR-1 | Runs fully offline with `LLM_PROVIDER=fake`, `VECTOR_STORE=memory` | §8, §13 | 1 |
| NFR-2 | Structured outputs everywhere (Pydantic models, no free-text parsing) | §6, §18 | 1 |
| NFR-3 | No secrets in code, git, logs or test output | §9, §18 | 1 |
| NFR-4 | FastAPI on port 8000, Next.js on port 3000 | §4.2, §11 | 1, 12 |
| NFR-5 | Every PRD row covered by ≥1 test; eval thresholds pass | §13 | 13 |
| NFR-6 | Docker Compose (frontend, backend, Redis, Qdrant) | §15 | 13 |
| NFR-7 | Terraform modules for AWS, Azure, GCP | §15 | 13 |

## Data Model (Core Tables)

| Table | Purpose | Phase |
|-------|---------|-------|
| `users` | Auth, roles | 3 |
| `tickets` | Lifecycle, status | 4 |
| `customers` | Name, email, workspace | 2 |
| `subscriptions` | Plan, billing_cycle, status | 2 |
| `workspaces` | Team metadata | 2 |
| `messages` | Ticket message log | 4 |
| `knowledge_articles` | Raw KB articles | 5 |
| `knowledge_chunks` | Chunked, embedded text | 5 |
| `workflow_events` | Node-level tracing | 9 |
| `approvals` | Pause/resolve records | 10 |
| `escalations` | Human-handoff records | 10 |
| `memory_notes` | Post-resolution notes | 11 |
| `audit_log` | Immutable actions | 3 |
| `tool_calls` | Recorded tool invocations | 6 |
| `settings` | Config key/value | 13 |

## Phase Dependencies

```
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13
```

Each phase must pass `make test` and `make demo` (where applicable) before the next begins.

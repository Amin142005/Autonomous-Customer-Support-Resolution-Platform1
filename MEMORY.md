# MEMORY – Locked Facts & Status

Last updated: 2026-11-19

---

## Locked Facts (do not change without an explicit design decision)

| # | Fact | Source |
|---|------|--------|
| 1 | Backend: Python 3.12+ (project stub uses `>=3.13` in pyproject.toml; will adjust to match §4.1 if needed) | CLAUDE.md §4.1 |
| 2 | Frontend: Next.js 15, React 19, TypeScript | CLAUDE.md §11 |
| 3 | Framework: LangGraph + LangChain | CLAUDE.md §4.1 |
| 4 | Web framework: FastAPI | CLAUDE.md §4.2 |
| 5 | Vector DB: Qdrant (preferred) or any HNSW-compatible store; `memory` backend for tests | CLAUDE.md §8 |
| 6 | Cache: Redis (required) | CLAUDE.md §8 |
| 7 | Database: SQLite for dev, PostgreSQL for prod | CLAUDE.md §4.3 |
| 8 | Roles: viewer (1) < agent (2) < admin (3) | CLAUDE.md §2 |
| 9 | LLM provider: OpenAI, Ollama, or `fake` — all selectable via `LLM_PROVIDER` env var | CLAUDE.md §13, §16 |
| 10 | Structured outputs (Pydantic models) required for **all** agent responses — no free-text parsing | CLAUDE.md §6 |
| 11 | Company: CloudDesk (SaaS — team collaboration, cloud storage, billing, workspaces, API) | CLAUDE.md §1 |
| 12 | 10 ticket categories: billing_inquiry, service_outage, account_access, plan_upgrade, plan_downgrade, data_export, integration_issue, bug_report, feature_request, refund_request | CLAUDE.md §6 |
| 13 | 13 build phases, sequential | CLAUDE.md §18 |
| 14 | Eval thresholds: classification ≥ 0.80, retrieval ≥ 0.75, escalation ≥ 0.90, citation ≥ 0.90 | CLAUDE.md §13 |

---

## Honest Status

| Area | Status | Notes |
|------|--------|-------|
| PLAN.md | ✅ Complete | Requirement catalog with phases |
| PLAN_PHASE.md | ✅ Complete | 13 phases detailed |
| Phase 1–13 | ⏳ Not started | No backend code beyond stub `main.py` |
| Frontend | ⏳ Not started | No `frontend/` directory |
| Tests | ⏳ Not started | No test framework configured |
| Makefile | ⏳ Not started | Not created |
| .env.example | ⏳ Not started | Not created |
| API_CONTRACT.md | ⏳ Not started | Not created |
| Eval cases | ⏳ Not started | Not created |
| Docker Compose | ⏳ Not started | Not created |
| Terraform | ⏳ Not started | Not created |
| CI workflows | ⏳ Not started | Not created |
| KB articles | ⏳ Not started | Not created |
| Demo users | ⏳ Not seeded | admin, sam, vic passwords TBD |

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-11-19 | Sequential phases (not parallel) | CLAUDE.md §18 mandates sequential build, each phase must pass before next |
| 2026-11-19 | SQLite for dev, PostgreSQL for prod | CLAUDE.md §4.3 |
| 2026-11-19 | `fake` LLM provider for all local testing | CLAUDE.md §16 — no LLM needed for unit tests |
| 2026-11-19 | Pydantic v2 for all schemas | FastAPI uses Pydantic v2 by default |
| 2026-11-19 | No new dependencies until Phase 1 begins | Keep project clean until scaffolding is approved |

---

## Current Session Notes

- PLAN.md, PLAN_PHASE.md, MEMORY.md, and SKILL.md created as initial project files per CLAUDE.md §19.
- Next step: Phase 1 (runtime skeleton) when the user begins building.

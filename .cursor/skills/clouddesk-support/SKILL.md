# SKILL – CloudDesk Support Platform Agent Procedure

**Project:** Autonomous Customer Support & Resolution Platform (CloudDesk)  
**Trigger:** "clouddesk-support", "build phase N", "next phase", "run demo", "run eval"

---

## 0. Pre-flight

1. **Read `CLAUDE.md`** — it is the single source of truth. If SKILL.md conflicts with CLAUDE.md, CLAUDE.md wins.
2. **Read `MEMORY.md`** — check honest status, locked facts, decisions log. Update at the end of every session.
3. **Read `PLAN_PHASE.md`** — find the current phase, its files, PRD rows, tests, demo, and exit criteria.
4. **Read `PLAN.md`** — cross-reference requirement IDs if the user mentions specific F/NFR numbers.

---

## 1. Start a Phase

```
Given a phase number N:
  a. Read the corresponding section in PLAN_PHASE.md.
  b. Read the full CLAUDE.md sections referenced by the phase (e.g. §4.1 for stack, §6 for agents).
  c. List the files to create in order of dependency.
  d. Create each file in order, matching existing style.
  e. Run `make test` (or the phase-specific test command).
  f. Run `make demo` where the phase defines a demo checkpoint.
  g. If anything fails, fix the root cause and re-run. Do not move on until the phase passes.
  h. Update MEMORY.md: mark the phase complete, add any decisions.
```

---

## 2. Write Code — Rules

- **Structured outputs only.** Every agent returns a Pydantic model. Never parse free text from the LLM.
- **No real secrets.** Use `fake` provider, mock tools, and in-memory vector stores for all local work.
- **Deterministic tests.** No network calls, no sleeps, no randomness in tests. Use fixtures and mocks.
- **Role checks.** Every write endpoint must call `require_role`.
- **Audit trail.** Every mutation (create, update, approve, reject, escalate) logs to `audit_log`.
- **Type hints.** All public functions get type hints (PEP 8 / `python` project rule).
- **JSON logging.** All log output is structured JSON with `request_id` and `level`.

---

## 3. File Naming & Conventions

| What | Convention | Example |
|------|------------|---------|
| Backend modules | lowercase with underscores | `backend/app/agents/supervisor.py` |
| Frontend components | PascalCase `.tsx` | `frontend/src/components/ui/StatusPill.tsx` |
| Tests | mirror source path under `tests/` | `tests/agents/test_supervisor.py` |
| Schemas | Pydantic models in `backend/app/schemas/` | `backend/app/schemas/tickets.py` |
| Routes | one file per resource in `backend/app/routes/` | `backend/app/routes/tickets.py` |
| Models | one file per table in `backend/app/models/` | `backend/app/models/ticket.py` |

---

## 4. Running Things

| Command | What it does |
|---------|-------------|
| `make backend` | Start FastAPI dev server on port 8000 |
| `make frontend` | Start Next.js dev server on port 3000 |
| `make test` | Run pytest (all phases) |
| `make test PHASE=5` | Run tests for a specific phase |
| `make demo` | Run the current phase demo scenario |
| `make demo TICKET=CD-1001` | Run demo with a specific ticket |
| `make seed` | Seed the database with demo data |
| `make ingest` | Chunk and index KB articles |
| `make docker` | Build and run Docker Compose |
| `make eval` | Run evaluation suite with threshold gating |

*(Defined in `Makefile` when Phase 1 starts.)*

---

## 5. Updating MEMORY.md

After every session, update `MEMORY.md`:
- Mark completed phases ✅
- Record new decisions in the Decisions Log table
- Note any blockers or questions in Current Session Notes
- Never change a Locked Fact without an explicit design decision

---

## 6. When Stuck

1. Re-read the relevant CLAUDE.md section.
2. Check `MEMORY.md` for past decisions.
3. Check `PLAN_PHASE.md` for the phase's exit criteria.
4. If the CLAUDE.md is silent on a detail, make a minimal, defensible choice and record it in MEMORY.md.
5. Ask the user only for things that genuinely block progress.

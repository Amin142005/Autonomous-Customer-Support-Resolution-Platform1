# Phase 1 — How It Works (Plain-English Guide)

> **For:** Recruiters, interview boards, and anyone who needs to understand what we built — without writing a single line of code.

---

## What Is This Project?

We are building an **AI-powered customer support system** for a fictional SaaS company called **CloudDesk**.

Imagine a company that sells cloud storage and collaboration tools. When customers send in support tickets (like "I can't log in" or "My bill is wrong"), this system reads the ticket, investigates the problem, finds the right answer from the company's knowledge base, and proposes a fix — all automatically. A human agent reviews and approves anything that costs money or changes an account.

**Phase 1** laid the foundation. Think of it as building the structure and plumbing before the walls and furniture go in. Without a strong foundation, the rest would not stand.

---

## The Four Building Blocks of Phase 1

Phase 1 has four parts. Each one solves a real problem that every production software system needs.

### 1. Settings & Logging (The Brain and the Journal)

#### Settings — `backend/app/core/config.py`

**What it does:** Every software system has settings — things like which database to use, how secure the login should be, or which AI provider (OpenAI, Ollama, etc.) to talk to. Instead of hard-coding these values into the code, we put them in **environment variables** — simple name-and-value pairs that can change between development, testing, and production without touching the code.

**How it works:** The `Settings` class reads these variables from the environment (or uses sensible defaults if none are set). A cached function `get_settings()` returns the same Settings object everywhere in the app, so we never re-read the environment more than once.

**Why it matters:** If you change a setting (like switching from OpenAI to a local AI model), you only change one file. The code stays the same. This is how professional systems stay flexible.

**Analogy:** Think of it like the control panel on a thermostat. You don't rewire the heater to change the temperature — you just turn a dial.

#### Logging — `backend/app/core/logging.py`

**What it does:** Every action in the system — who logged in, what request came in, what error occurred — is written to a **structured log file** in JSON format. JSON is a clean, machine-readable format that tools can search and analyse.

**How it works:** We use Python's built-in logging system, but we customised it to:
- Write every log entry as a structured JSON line (so tools can parse it)
- Rotate log files automatically when they grow too large (so the disk never fills up)
- Attach a unique **Request ID** to every log entry (so you can trace one user's request across the entire system)

**Why it matters:** When something goes wrong in production, the logs are the detective's notebook. Without them, debugging is like finding a needle in a haystack without a magnet.

**Analogy:** Think of it as a flight recorder (black box) for an airplane. You only need it when something goes wrong, but it tells you exactly what happened.

---

### 2. Health Checks & Request Tracing (The Pulse and the Passport)

#### Health Endpoints — `backend/app/main.py`

**What it does:** Two special API routes let external systems check if the application is alive and ready to work:

| Endpoint | What it tells you |
|---|---|
| `/health/live` | "Is the process running?" — A simple heartbeat check. |
| `/health/ready` | "Can it actually serve requests?" — Checks that the database, file system, and other dependencies are working. |

**How it works:** When a monitoring tool (or a load balancer) hits these endpoints, the app returns a short JSON response with its status, version, and a timestamp. The readiness check goes further and tests each dependency (database connection, file storage, etc.) and reports which ones are up and which are down.

**Why it matters:** In production, systems need to know when to restart themselves or when to stop sending traffic to a failing server. These endpoints are the "are you okay?" check that keeps the system self-healing.

**Analogy:** Think of it like a doctor checking your pulse (live) and then doing a full blood test (ready) to confirm you're fit for duty.

#### Request-ID Middleware — `backend/app/middleware/request_id.py`

**What it does:** Every single request that enters the system gets a **unique ID** — like a passport number for that request. If the request already has one, we keep it. If not, we generate one.

**How it works:** This is a piece of code that runs **before every request reaches the app logic**. It checks for an `X-Request-ID` header. If it's missing, it creates a new one. The ID is then attached to every log line and response for that request.

**Why it matters:** When you have thousands of requests happening at once, the logs become a mix of many conversations. With Request IDs, you can filter all log lines that belong to one specific request — turning chaos into order.

**Analogy:** Think of it like a ticket number at a help desk. When you call back, they look up your ticket number and see the whole history. No confusion.

---

### 3. Test Harness (The Safety Net)

#### Test Fixtures — `tests/conftest.py`

**What it does:** Before any feature code is trusted, it is tested. The test harness sets up a **clean, isolated testing environment** for every single test — with its own temporary files, mock settings, and a fake web server.

**How it works:**
- A `mock_settings` fixture creates settings that point to temporary folders (so tests never write to real log files or databases)
- A `_patch_settings` fixture overrides the app's settings so every test uses these safe mock settings automatically
- A `test_app` fixture builds a fresh FastAPI application for each test
- A `test_client` fixture provides a fake web browser that sends requests to the test app without needing a real server

**Why it matters:** Tests that share state (like writing to the same log file) will interfere with each other. Our setup guarantees that every test starts from scratch, runs in isolation, and leaves no trace. This means tests are **reliable and repeatable**.

**Analogy:** Think of it like a driving test. You get a clean car, a clear track, and a fresh set of rules — every time. You never inherit the previous candidate's mistakes.

#### Test Files — `tests/unit/test_*.py`

Three test files verify the Phase 1 code:

| Test file | What it tests |
|---|---|
| `test_health_endpoints.py` | That `/health/live` and `/health/ready` return correct responses |
| `test_request_id.py` | That every request gets a unique ID, and that existing IDs are preserved |
| `test_settings.py` | That settings load correctly, use defaults, and respect environment overrides |

In total, **22 tests pass** on every run. If any future change breaks existing functionality, these tests will catch it immediately.

---

### 4. Developer Tooling (The Instruction Manual)

#### Makefile — `Makefile`

**What it does:** Developers need to run many commands during development: install dependencies, start the server, run tests, check code style, clean up temporary files. The Makefile collects all these commands into simple, memorable names.

**How it works:** Instead of typing a long command like:
```
python -m uvicorn backend.app.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```
A developer simply types:
```
make run
```

| Command | What it does |
|---|---|
| `make install` | Install the project and all dependencies |
| `make run` | Start the development server |
| `make test` | Run all tests |
| `make dev` | Install, lint, and test in one go |
| `make clean` | Remove temporary files and caches |
| `make help` | Show all available commands |

**Why it matters:** When a new developer joins, they can get started in minutes instead of searching through documentation for the right commands.

**Analogy:** Think of it like the quick-start guide that comes with a new appliance. Instead of reading the whole manual, you follow three simple steps.

#### Environment Template — `.env.example`

**What it does:** This file lists every configuration setting the application needs, with sensible defaults and clear comments explaining each one. A developer copies it to `.env` and edits the values they need.

**How it works:** The file covers all categories of settings:
- **Application** (name, version, environment)
- **Server** (host, port, workers)
- **Database** (connection URLs)
- **AI / LLM** (provider choice, API keys, models)
- **Authentication** (JWT secrets and expiry)
- **Logging** (level, format, file size limits)
- **Integrations** (mock service toggles, knowledge base paths)

**Why it matters:** Without this, a developer would need to dig through source code to find which settings exist. The template is a one-stop reference.

**Analogy:** Think of it like a form with all the fields you need to fill in to open a bank account. The form tells you what goes where.

---

## How It All Fits Together

```
Environment variables (.env)
        │
        ▼
    Settings (config.py) ──→ Controls every part of the app
        │
        ├──→ Logging (logging.py) ──→ Writes structured, searchable logs
        │
        ├──→ Health endpoints (main.py) ──→ "Are we alive? Are we ready?"
        │
        ├──→ Request-ID middleware (request_id.py) ──→ Every request gets a unique tracker
        │
        └──→ Tests (tests/) ──→ Verify everything works in isolation
```

---

## Why This Matters to the Business

1. **Reliability:** The health checks mean the system can detect and recover from problems automatically. Downtime is reduced.
2. **Debuggability:** Structured logging and request tracing mean that when a customer reports an issue, support teams can find the root cause in minutes, not hours.
3. **Safety:** Automated tests catch regressions before they reach customers. The test harness ensures tests are trustworthy.
4. **Speed:** Developer tooling (Makefile, .env.example) means new team members become productive on day one, not after a week of figuring things out.
5. **Flexibility:** Environment-based configuration means the same code runs in development, staging, and production with zero changes — just different settings.

---

## Key Takeaway

Phase 1 did not build customer-facing features. It built the **infrastructure that makes those features possible, reliable, and maintainable**. It is the difference between a house with no foundation and one that can stand through storms.

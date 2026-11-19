# Phase 1 — Interview Q&A

> **CloudDesk Autonomous Customer Support & Resolution Platform**
> Phase 1: Foundation & Infrastructure

---

## A. Configuration & Settings

### Q1. How are application settings loaded? Where do they come from?

Settings are loaded via a Pydantic `BaseSettings` subclass in `backend/app/core/config.py`. Pydantic automatically reads values from:
1. **Environment variables** (e.g. `APP_NAME`, `APP_ENV`, `DATABASE_URL`) — highest priority.
2. **.env file** in the project root (fallback for local dev).
3. **Defaults** defined on each field (last resort).

The `Settings` class defines ~24 fields (app name, version, debug, log level, database URL, LLM API keys, etc.). A module-level singleton is returned by `get_settings()`.

### Q2. Why use Pydantic `BaseSettings` instead of `os.environ`?

- **Type safety:** values are typed (`bool`, `str`, `Path`) at the class level.
- **Validation:** Pydantic validates types on load; wrong types raise early.
- **Computed properties:** e.g. `cors_origins_list` splits a comma-separated string into a `list[str]` via `@property`.
- **Centralisation:** one class instead of scattered `os.environ.get("X", "default")` calls.
- **Testability:** you can instantiate `Settings(...)` with explicit values in tests without touching environment variables.

### Q3. How does the CORS origin list work?

`CORS_ORIGINS` is a single comma-separated string (e.g. `"http://localhost:3000,http://example.com"`). The `@property cors_origins_list` splits on `,` and strips whitespace. A single `"*"` becomes `["*"]`, enabling wildcard CORS.

### Q4. What is the purpose of `get_settings()`? Why not just import `Settings` directly?

`get_settings()` returns a cached `Settings` instance so the settings are loaded once per process. FastAPI's `Depends(get_settings)` injects that same instance into every route/test. In tests we `override_dependency(get_settings, lambda: mock_settings)` to swap in test values without touching `.env` or environment variables.

### Q5. What happens if a required environment variable is missing?

Fields without a `default` will raise a `ValidationError` at startup if the env var or .env value is absent. Fields with a `default` silently use the default. This makes the startup fail-fast for truly required values (e.g. database URL in production).

---

## B. Logging

### Q6. How does the logging pipeline work?

`setup_logging()` in `backend/app/core/logging.py` configures the root logger based on settings:

| Setting | Effect |
|---|---|
| `LOG_LEVEL` | Root logger level (`DEBUG`, `INFO`, etc.) |
| `LOG_FORMAT=json` | `JsonFormatter` — structured JSON with timestamp, level, message, extra fields |
| `LOG_FORMAT=plain` | `logging.Formatter` — human-readable `% (asctime)s - %(name)s - %(levelname)s - %(message)s` |
| `LOG_FILE` | `TimedRotatingFileHandler` writes to the path; rotates daily, keeps 7 days |
| `LOG_TO_CONSOLE` | `StreamHandler(sys.stdout)` for real-time terminal output |

### Q7. Why two log formats (JSON and plain)?

- **JSON** (`LOG_FORMAT=json`): parseable by log aggregators (ELK, Datadog). Each line is a structured record with fields like `{"timestamp": "...", "level": "INFO", "message": "...", "request_id": "..."}`.
- **Plain** (`LOG_FORMAT=plain`): human-readable for local development.

### Q8. How does log rotation work?

A `TimedRotatingFileHandler` rotates daily (`when="midnight"`, `interval=1`) and keeps 7 backup files (`backupCount=7`). Old logs are automatically deleted after 7 days. This prevents unbounded disk growth.

### Q9. How do you add extra fields (e.g. `request_id`) to every log line?

The `enrich(logger, **extra)` function calls `logger.extra = extra`. The `JsonFormatter` merges these extras into every JSON log record. The `RequestIdMiddleware` calls this so every log line during request processing carries the request ID.

---

## C. Application Lifecycle & Startup

### Q10. What happens when the FastAPI app starts?

`main.py` uses the FastAPI **lifespan** pattern:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    logger.info("Shutting down")
```

Steps on startup:
1. Load `Settings` from env/.env.
2. Configure logging (formatters, handlers, rotation).
3. Log a startup message with app name and version.
4. On shutdown, log a shutdown message and clean up handlers.

### Q11. Why use the lifespan context manager instead of `on_event("startup")`?

The lifespan pattern (PEP 567 async context manager):
- Is the **modern** FastAPI approach (`on_event` is deprecated).
- Supports both setup (`yield` before) and teardown (`yield` after) in one place.
- Is easy to test: `TestClient` enters and exits the lifespan automatically.
- Avoids global state leaks between tests.

### Q12. What is the role of `create_app()`?

`create_app()` is a factory function that returns the configured FastAPI instance. It:
1. Creates the `FastAPI` app with the lifespan manager.
2. Adds middleware (CORS, Request-ID).
3. Registers routes (health endpoints).
4. Returns the app.

This pattern is used by both `uvicorn` (in production) and the test fixtures (to create isolated app instances per test file).

---

## D. Middleware

### Q13. What does `RequestIdMiddleware` do?

For every incoming HTTP request:
1. Check if the request already has an `X-Request-ID` header.
2. If yes, preserve it (supports distributed tracing from upstream proxies).
3. If no, generate a new UUID v4.
4. Add `X-Request-ID` to the **response** headers so the client can correlate logs.
5. Call `enrich(logger, request_id=...)` so every log line during this request carries the ID.

### Q14. Why is `X-Request-ID` important?

In a distributed system, a single user request may touch many services. A unique request ID lets you trace all log lines belonging to that request across services. Even in Phase 1 (single process), the habit is established for later phases where multiple microservices will share this ID.

### Q15. What is the middleware execution order?

```
Request → CORSMiddleware → RequestIdMiddleware → Router → Response
```

CORS runs first (it modifies headers on both request and response). Request-ID runs second (it enriches logging). The router matches the path to a handler last.

### Q16. Why is CORS middleware added before RequestIdMiddleware?

FastAPI's `add_middleware()` adds middleware in **reverse** order — the last call to `add_middleware` wraps the innermost layer. CORS needs to run on every request (including preflight `OPTIONS`) before any logic, so it's added first in code (outermost in execution).

---

## E. Health Endpoints

### Q17. What are the two health endpoints and why two?

| Endpoint | Purpose | Returns |
|---|---|---|
| `GET /health/live` | **Liveness** probe — is the process alive? | `{"status": "ok"}` |
| `GET /health/ready` | **Readiness** probe — is the app ready to serve? (checks DB, external deps) | `{"status": "ready", "version": "..."}` |

Kubernetes uses liveness to restart dead pods and readiness to route traffic. In Phase 1, both are simple since there are no external dependencies yet.

### Q18. What does `/health/ready` check?

In Phase 1 it only returns `{"status": "ready", "version": settings.APP_VERSION}`. In later phases it will check database connectivity, LLM API reachability, and other dependencies.

---

## F. Testing

### Q19. How does the test harness work?

Three key fixtures in `tests/conftest.py`:

| Fixture | What it does |
|---|---|
| `mock_settings` | Creates a `Settings` instance with a `tmp_path`-based log directory so no real files are written. |
| `test_app` | Calls `create_app()`, then `app.dependency_overrides[get_settings] = lambda: mock_settings` to inject test settings. |
| `test_client` | Wraps `test_app` in `httpx.AsyncClient` for async test requests. |

### Q20. Why override `get_settings` in tests instead of setting environment variables?

- **Isolation:** each test file gets its own `Settings` with no cross-test pollution.
- **Speed:** no need to modify and restore `os.environ`.
- **Safety:** no risk of leaking test secrets into the real environment.
- **Determinism:** test values are explicit in the fixture, not hidden in `.env`.

### Q21. What does the `cache_clear()` call do in the test setup?

`get_settings` is cached (the module-level `_settings` variable). `cache_clear()` resets it so the next call creates a fresh instance. Without this, the first test would set the cached value and subsequent tests would see stale settings.

### Q22. How many tests exist in Phase 1? What do they cover?

22 tests across 3 files:
- **`test_health_endpoints.py`** (5 tests): liveness returns 200 + `{"status":"ok"}`, readiness returns 200 + version, both include `X-Request-ID`.
- **`test_settings.py`** (8 tests): defaults, overrides, CORS parsing, log level, app name/version, database URL, log format.
- **`test_request_id.py`** (5 tests): auto-generates UUID v4, preserves custom IDs, unique per request, case-insensitive header, readiness endpoint also gets ID.

(Plus 4 more tests in settings for edge cases.)

---

## G. Routing

### Q23. How are routes registered?

Two routes are registered directly on the FastAPI app (no separate router files yet):

```python
@app.get("/health/live")
async def health_live():
    return {"status": "ok"}

@app.get("/health/ready")
async def health_ready(settings: Settings = Depends(get_settings)):
    return {"status": "ready", "version": settings.APP_VERSION}
```

Phase 1 keeps routing simple. Later phases will introduce API routers (`/api/v1/tickets`, `/api/v1/customers`, etc.) in separate modules.

### Q24. Why prefix health endpoints and not API endpoints?

Health endpoints (`/health/*`) are infrastructure probes, not business API. API endpoints will use `/api/v1/...` with versioning. This separation is a standard practice.

---

## H. Project Structure & Conventions

### Q25. What is the project directory structure?

```
backend/
  app/
    core/          # config.py, logging.py, security.py (planned)
    middleware/    # request_id.py
    main.py        # FastAPI factory, lifespan, routes
    __init__.py
  __init__.py
tests/
  conftest.py      # shared fixtures
  unit/
    test_health_endpoints.py
    test_settings.py
    test_request_id.py
.env.example       # template with all Settings fields
Makefile           # dev targets
pyproject.toml     # dependencies, project metadata
```

### Q26. Why split `core/` and `middleware/` as subpackages?

- `core/` holds cross-cutting concerns (config, logging, security) used by many parts.
- `middleware/` holds ASGI middleware classes, isolated so they can be imported independently.
- Clear separation makes it easy to find where a concern lives as the project grows.

### Q27. What is the purpose of the `__init__.py` files?

They mark directories as Python packages so imports work (`from backend.app.core.config import Settings`). They are minimal (docstring only) to avoid side effects at import time.

---

## I. Dev Tooling

### Q28. What does the Makefile do?

| Target | Command | Purpose |
|---|---|---|
| `install` | `pip install -e .` | Install the project in editable mode with all dependencies |
| `run` | `uvicorn backend.app.main:create_app --factory --reload` | Start dev server with auto-reload |
| `test` | `pytest -v` | Run the full test suite |
| `lint` | `ruff check backend/ tests/` | Run linter |
| `format` | `ruff format backend/ tests/` | Auto-format code |
| `clean` | `rm -rf logs/ __pycache__ .pytest_cache` | Clean generated files |

### Q29. Why use `--factory` with uvicorn?

`create_app()` is a factory function (returns a FastAPI instance). `--factory` tells uvicorn to call it. Without `--factory`, uvicorn expects the app instance directly. This pattern allows per-process app customisation (different settings per instance).

### Q30. What is in `.env.example`?

A template listing every `Settings` field with example values and comments. Developers copy it to `.env` and fill in real values. It is **not** git-ignored (`.env` is).

---

## J. Security

### Q31. How are secrets handled in Phase 1?

Secrets (API keys, passwords, JWT secret) are:
1. Defined as `Settings` fields with no default.
2. Loaded from environment variables or `.env` at startup.
3. Never logged (the `JsonFormatter` excludes fields containing "password", "secret", "key", "token").
4. `.env` is in `.gitignore`; only `.env.example` is committed.

### Q32. Is SQL injection a concern in Phase 1?

Phase 1 has no database queries yet. When database access is added, the project rule enforces **parameterised queries only** — no string formatting for SQL.

### Q33. How does CORS protect the app?

CORS middleware restricts which origins can make cross-origin requests. In development `CORS_ORIGINS="*"` is allowed; in production it should be set to specific origins (e.g. `"https://app.clouddesk.com"`).

---

## K. Architecture & Design Decisions

### Q34. Why FastAPI over Flask or Django?

- **Async native:** `async def` endpoints, async test clients — essential for I/O-bound AI workloads (LLM calls, DB queries).
- **Type hints:** automatic request/response validation via Pydantic.
- **Dependency injection:** built-in `Depends()` for settings, DB sessions, auth.
- **Performance:** Starlette + uvicorn handle high concurrency.
- **Documentation:** auto-generated OpenAPI/Swagger UI.

### Q35. Why in-process architecture for Phase 1?

Phase 1 establishes the foundation: settings, logging, middleware, health checks, and test harness. No external services (DB, message queue, LLM API) are connected yet. This keeps the foundation **testable offline** and **fast to iterate**. Later phases add external dependencies one at a time.

### Q36. How does the pipeline architecture (from CLAUDE.md) relate to Phase 1?

The pipeline (`Understand → Classify → Investigate → ... → Remember`) is the **business logic** that will run inside the FastAPI app. Phase 1 builds the **infrastructure** (settings, logging, middleware, health) that the pipeline will run on top of. Phase 2+ will add the pipeline stages.

### Q37. What would you change if the project needed Docker from the start?

- Add a `Dockerfile` based on `python:3.13-slim`.
- Add a `docker-compose.yml` with services: app, postgres, redis.
- Change `DATABASE_URL` to use Docker service names (`postgres://postgres:password@db:5432/clouddesk`).
- The core code (`config.py`, `logging.py`, `main.py`) would need **no changes** — environment variables work the same inside Docker.

---

## L. Edge Cases & Troubleshooting

### Q38. What happens if the log directory doesn't exist?

`setup_logging()` calls `path.parent.mkdir(parents=True, exist_ok=True)` before creating the `TimedRotatingFileHandler`. The directory is created automatically.

### Q39. What happens if two requests have the same custom `X-Request-ID`?

The middleware **preserves** the client-supplied ID without validation. This is intentional: an upstream proxy may send the same ID for retries. The logging system does not deduplicate — it trusts the ID.

### Q40. What if `LOG_FORMAT` is set to an unknown value?

The code defaults to plain text format for any value other than `"json"`. This is a safe fallback — the app won't crash on an unknown format.

### Q41. How do you debug a failing test?

1. Run `pytest -v tests/unit/test_xxx.py` to see the specific failure.
2. Check the assertion error for the expected vs actual value.
3. If the test uses `test_client`, check that the endpoint returns the expected status code and body.
4. Remember: tests run against `mock_settings`, not the real `.env`.

### Q42. Why do health endpoint tests check for `X-Request-ID` in the response?

To verify the middleware is correctly applied to all routes. If a route somehow bypassed the middleware, the header would be missing and the test would catch it.

---

## M. Future Phases

### Q43. What infrastructure changes are expected in Phase 2?

- **Database:** add PostgreSQL connection, Alembic migrations, `get_db()` dependency.
- **Auth:** JWT-based authentication, OAuth2 password flow, `require_role` middleware.
- **New routes:** `/api/v1/tickets`, `/api/v1/customers`, `/api/v1/knowledge`.
- **Test fixtures:** `test_db`, `test_user`, `test_ticket`.

### Q44. What changes in Phase 3+?

- **LLM integration:** API calls to external AI services, retry logic, timeout handling.
- **Message queue:** async job processing for long-running ticket resolution.
- **Caching:** Redis for knowledge base results.
- **Monitoring:** metrics endpoints, structured log aggregation.
- **Docker:** containerisation, multi-stage builds, health check integration.

---

*End of Phase 1 Interview Q&A — 44 questions covering configuration, logging, middleware, lifecycle, testing, routing, security, architecture and troubleshooting.*

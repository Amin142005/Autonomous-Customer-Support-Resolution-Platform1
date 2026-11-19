# CloudDesk Support — Makefile
#
# Targets for local development.  Run with `make <target>` (GNU make / WSL)
# or `nmake /f Makefile <target>` on Windows.  On Windows without WSL the
# commands use Python directly so a venv is expected to be active.

PYTHON  := python
PIP     := python -m pip
UVICORN := python -m uvicorn
PYTEST  := python -m pytest
RUFF    := python -m ruff

# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------

install: ## Install the project in editable mode with dev dependencies
	$(PIP) install -e ".[dev,test]"

.PHONY: install

# ---------------------------------------------------------------------------
# Running the app
# ---------------------------------------------------------------------------

run: ## Start the dev server (hot-reload)
	$(UVICORN) backend.app.main:create_app --factory --reload --host 0.0.0.0 --port 8000

run-release: ## Start the server in release mode (no hot-reload)
	$(UVICORN) backend.app.main:create_app --factory --host 0.0.0.0 --port 8000 --workers 1

.PHONY: run run-release

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

test: ## Run the full test suite
	$(PYTEST) -v

test-cov: ## Run tests with coverage report
	$(PYTEST) -v --cov=backend.app --cov-report=term-missing --cov-report=html

.PHONY: test test-cov

# ---------------------------------------------------------------------------
# Linting & formatting
# ---------------------------------------------------------------------------

lint: ## Run ruff linter
	$(RUFF) check backend/app tests

lint-fix: ## Auto-fix linting issues
	$(RUFF) check --fix backend/app tests

format: ## Format code with ruff
	$(RUFF) format backend/app tests

.PHONY: lint lint-fix format

# ---------------------------------------------------------------------------
# Housekeeping
# ---------------------------------------------------------------------------

clean: ## Remove generated files and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage .pytest_cache

clean-db: ## Remove local SQLite databases
	rm -f data/support.db data/checkpoints.db

clean-logs: ## Remove log files
	rm -f logs/*.log

.PHONY: clean clean-db clean-logs

# ---------------------------------------------------------------------------
# Full dev cycle (install → lint → test)
# ---------------------------------------------------------------------------

dev: install lint test ## Install, lint, and test in one step

.PHONY: dev

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: help

<!-- Written by Euron Code after each task. It is rewritten automatically: put your own rules in
     another file in .euron/rules/. -->

# Learned in this project

- Tests: `.\.venv\Scripts\python.exe -m pytest -v 2>&1` works here (passed 2x, last 2026-11-19). Use it to verify changes.
- Tests: `.\.venv\Scripts\python.exe -m pip install pytest pytest-asyncio httpx` works here (passed 1x, last 2026-11-19). Use it to verify changes.

## Security (from .euron/security/assessment.md)
- This code base has had: debug mode on (SEC043). Turn debug off outside local development; it leaks stack traces and can allow code execution. Do not add more; fix the existing ones when you touch those files.

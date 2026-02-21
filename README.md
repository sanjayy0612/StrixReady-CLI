# Strix CLI

Strix is a Python command‑line tool that scans a GitHub repository, generates necessary configuration files using AI, and spins up a development environment with Docker Compose.

## Development Overview

This repository is currently in active development. The goal is to provide a **developer-friendly CLI** named `strix` that can inspect a GitHub repository, infer its technology stack, and automatically generate the necessary containerization and environment files via an AI backend.

You’ll find the work split across two main packages (`cli` and `backend`) plus some static templates. Below is the workflow and component responsibilities, designed to help your team understand what to build and how the pieces fit together.

---

### Workflow (high level)

1. **User invokes CLI** with a GitHub URL (`strix <url>`).
2. CLI clones the repo locally (implementation in `analyzer`).
3. Analyzer inspects files (`requirements.txt`, `Dockerfile`, `package.json`, etc.) and builds a profile containing languages, frameworks, ports, databases, etc.
4. The profile is sent to an AI service (OpenAI or Claude) in `generator.generate`.
5. AI returns a set of text artifacts: a `Dockerfile`, `docker-compose.dev.yml`, `.env.example`, and a `PROJECT.md` detailing the project.
6. CLI writes these files into the target repository, then uses `subprocess` to run `docker compose` and spin up the environment.
7. The `doctor` command calls `health.check_all` to ping the running API and any database connections, reporting status using Rich output.

> **Note:** AI integration is stubbed at the moment; replace the placeholder with actual API calls and prompt engineering logic.

---

### Package breakdown

#### `strix/cli`

- **`main.py`** – entrypoint for the Typer CLI.
  - `scan` command orchestrates analysis, generation, writing of files, and starting Docker.
  - `doctor` command invokes health checks and prints colored results.
  - Uses [Rich](https://github.com/Textualize/rich) for spinners and stylistic output.

#### `strix/backend`

- **`analyzer.py`** – responsible for cloning the repo (e.g. via `git`), reading key files, and constructing a dictionary representing the project. Add parsers for languages, frameworks, DB URLs, exposed ports, etc.
- **`generator.py`** – encapsulates AI logic. Currently returns hardcoded strings. Later integrate with `openai` or Claude API:
  ```python
  from openai import OpenAI
  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
  response = client.responses.create(...)
  ```
  The AI prompt should include the profile and ask for formatted files.
- **`health.py`** – lightweight checks using `requests` for HTTP and stubbed DB connectivity. Expand to support specific drivers.
- **`main.py`** – simple FastAPI app used for internal health endpoints or extensions.

#### `tesis/templates`

Stores static examples that serve as starting seeds for generated content. They are **not** used at runtime but can be referenced by generator logic or tests.

- `devcontainer.json` – example for VS Code dev containers; useful when preparing the CLI repo itself.
- `docker-compose.yml` – baseline compose file showing service structure; used for documentation or AI examples.

> Generated output files will live in the target repository and are named:
> - `Dockerfile`
> - `docker-compose.dev.yml`
> - `.env.example`
> - `PROJECT.md`

---

### Project structure (for quick reference)
```
strix/
├── cli/
│   ├── __init__.py
│   └── main.py          # Typer commands & Rich output
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI app (health endpoints)
│   ├── analyzer.py      # inspect & profile target repo
│   ├── generator.py     # AI prompt/response handling + file writer
│   └── health.py        # ping API/DB for "doctor" command
├── templates/           # static examples and devcontainer
│   ├── devcontainer.json
│   └── docker-compose.yml
├── pyproject.toml       # packaging metadata
├── requirements.txt     # development dependencies
└── README.md            # developer-centric documentation
```

---

### AI Integration

- **Where?** In `backend/generator.py`.
- **What?** Your AI model should take a JSON-like profile produced by `analyzer.analyze_repo()` and return strings for the four output files.
- **How to test:** stub the `generate` function to return predictable content, then verify `write_artifacts` writes correctly and the CLI is able to start Docker.
- **Future enhancements:** Add caching, prompt templates, and support for multiple AI providers.

---

### Running & iterating locally

```bash
# from workspace root
python -m venv .venv
source .venv/bin/activate
pip install -e strix  # editable install makes CLI available as `strix`
```

To invoke the backend FastAPI app directly (useful for debugging health checks):
```bash
uvicorn strix.backend.main:app --reload
```

Unit tests aren’t included yet—plan for `pytest` with fixtures that mock `subprocess`, `requests`, and AI responses.

---

### Tips for new contributors

- Start by fleshing out `analyzer` logic; it’s the foundation of the flow.
- Keep the CLI dumb; let the backend modules encapsulate business logic.
- Add type hints and run `mypy`/`flake8` frequently.
- Document any new environment variables (e.g. `OPENAI_API_KEY`) in `.env.example` once generated.

---

More walkthroughs, diagrams, and onboarding notes can be added as the tool matures. This README should serve as the single source of truth for developers stepping into the project.
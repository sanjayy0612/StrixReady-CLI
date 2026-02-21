# Strix CLI

Strix is a Python command‑line tool that scans a GitHub repository, generates necessary configuration files using AI, and spins up a development environment with Docker Compose.

## Features

- Analyze project language, framework, dependencies and ports
- Use AI (OpenAI/Claude) to generate Dockerfile, docker-compose.yml, .env example, and documentation
- Provide `strix doctor` to verify service health

## Installation

```bash
pip install .
```

## Usage

```bash
strix <github-url>
strix doctor
```

## Project structure

```
strix/
├── cli/
│   ├── __init__.py
│   └── main.py          # Typer CLI commands
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── analyzer.py      # Repo file scanner/detector
│   ├── generator.py     # AI config generator
│   └── health.py        # Health check logic
├── templates/
│   ├── devcontainer.json
│   └── docker-compose.yml
├── pyproject.toml       # For pip publishing
├── requirements.txt
└── README.md
```

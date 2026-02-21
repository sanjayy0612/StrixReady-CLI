import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any


def _repo_name_from_url(repo_url: str) -> str:
    tail = repo_url.rstrip("/").split("/")[-1]
    if tail.endswith(".git"):
        tail = tail[:-4]
    return tail or "repo"


def _prepare_repo_path(repo_url: str) -> Path:
    candidate = Path(repo_url).expanduser()
    if candidate.exists() and candidate.is_dir():
        return candidate.resolve()

    parent = Path(tempfile.mkdtemp(prefix="strix_repo_"))
    repo_name = _repo_name_from_url(repo_url)
    target_path = parent / repo_name
    subprocess.run(["git", "clone", repo_url, str(target_path)], check=True)
    return target_path.resolve()


def analyze_repo(repo_url: str) -> Dict[str, Any]:
    """Clone/resolve a repository and return a lightweight profile."""
    local_path = _prepare_repo_path(repo_url)

    languages = []
    frameworks = []
    ports = []

    if (local_path / "requirements.txt").exists() or (local_path / "pyproject.toml").exists():
        languages.append("python")
    if (local_path / "package.json").exists():
        languages.append("javascript")
    if (local_path / "Dockerfile").exists():
        frameworks.append("docker")

    profile = {
        "url": repo_url,
        "local_path": str(local_path),
        "repo_name": local_path.name,
        "languages": languages,
        "frameworks": frameworks,
        "database": None,
        "ports": ports,
    }
    return profile

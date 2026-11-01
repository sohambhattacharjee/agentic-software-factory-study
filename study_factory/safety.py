import json
import os
import stat


STUDY_ID = "synthetic-brownfield-agentic"
MARKER = ".research-scope.json"
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", "runs", "node_modules", "dist", "build"}
SENSITIVE_NAMES = {".env", ".env.local", "id_rsa", "id_ed25519", "credentials", "secrets.json"}
MAX_FILE_BYTES = 40_000
MAX_CONTEXT_BYTES = 100_000


class SafetyError(ValueError):
    pass


def require_study_repo(repo_path):
    root = os.path.realpath(repo_path)
    if not os.path.isdir(root):
        raise SafetyError("Target path must be an existing directory.")
    marker_path = os.path.join(root, MARKER)
    try:
        with open(marker_path, encoding="utf-8") as marker_file:
            marker = json.load(marker_file)
    except (OSError, json.JSONDecodeError) as exc:
        raise SafetyError("Target is not marked as the independent synthetic study repository.") from exc
    if marker.get("study_id") != STUDY_ID or marker.get("data_classification") != "synthetic-only":
        raise SafetyError("Target marker does not match the independent synthetic study.")
    return root


def safe_relative_path(path):
    if not isinstance(path, str) or not path or "\x00" in path:
        raise SafetyError("Edit path must be a non-empty relative path.")
    normalized = path.replace("\\", "/")
    parts = normalized.split("/")
    if normalized.startswith("/") or any(part in ("", ".", "..") for part in parts):
        raise SafetyError("Edit paths cannot be absolute or traverse directories.")
    if any(part in EXCLUDED_DIRS or part in SENSITIVE_NAMES for part in parts):
        raise SafetyError("Edit path targets an excluded or sensitive location.")
    return os.path.join(*parts)


def is_regular_text_file(path):
    try:
        info = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISREG(info.st_mode) and info.st_size <= MAX_FILE_BYTES


def should_exclude(name):
    return name in EXCLUDED_DIRS or name in SENSITIVE_NAMES or name.endswith(
        (".pem", ".key", ".p12", ".pfx", ".sqlite", ".sqlite3", ".db", ".pyc")
    )

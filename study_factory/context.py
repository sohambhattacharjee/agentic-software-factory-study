import hashlib
import os

from .safety import MAX_CONTEXT_BYTES, MAX_FILE_BYTES, should_exclude


PREFERRED_NAMES = {"README.md", "pyproject.toml", "requirements.txt", "package.json", "Makefile", "AGENTS.md", ".research-scope.json"}
TEXT_SUFFIXES = {".py", ".md", ".toml", ".json", ".yaml", ".yml", ".ini", ".cfg", ".txt", ".sh"}


def inventory(root):
    entries = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not should_exclude(d) and not d.startswith("."))
        for name in sorted(files):
            if should_exclude(name):
                continue
            full = os.path.join(current, name)
            relative = os.path.relpath(full, root).replace(os.sep, "/")
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            entries.append({"path": relative, "bytes": size, "suffix": os.path.splitext(name)[1].lower()})
    return entries


def select_context(root, with_map):
    entries = inventory(root)
    if with_map:
        candidates = [entry["path"] for entry in entries if entry["suffix"] in TEXT_SUFFIXES]
    else:
        candidates = [entry["path"] for entry in entries if os.path.basename(entry["path"]) in PREFERRED_NAMES]
        candidates += [entry["path"] for entry in entries if entry["path"].startswith("app/") and entry["suffix"] == ".py"]
    selected = []
    parts = []
    total = 0
    for relative in sorted(set(candidates)):
        full = os.path.join(root, relative)
        if not os.path.isfile(full) or os.path.islink(full):
            continue
        size = os.path.getsize(full)
        if size > MAX_FILE_BYTES or total + size > MAX_CONTEXT_BYTES:
            continue
        try:
            with open(full, "r", encoding="utf-8") as source:
                content = source.read()
        except (UnicodeError, OSError):
            continue
        selected.append({"path": relative, "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(), "bytes": len(content.encode("utf-8"))})
        parts.append("\n--- FILE: " + relative + " ---\n" + content)
        total += len(content.encode("utf-8"))
    return entries, selected, "".join(parts)

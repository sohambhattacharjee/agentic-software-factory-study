import difflib
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

from .context import select_context
from .profiles import PROFILES
from .safety import MAX_FILE_BYTES, SafetyError, is_regular_text_file, require_study_repo, safe_relative_path


SYSTEM_INSTRUCTIONS = """You are implementing a small change in an independently created synthetic research application. Use only the supplied repository context. Return one JSON object, with no markdown fences, in this exact shape: {\"summary\": string, \"edits\": [{\"path\": relative_path, \"content\": complete_file_text}], \"risks\": [string]}. Do not propose shell commands, secrets, external services, commits, or edits outside the repository. Preserve existing behavior unless the task requires a change. If you cannot safely implement the task from the supplied context, return an empty edits array and explain why in summary."""


def _parse_result(text):
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Provider output must be a JSON object without markdown fences.") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("edits"), list):
        raise ValueError("Provider output must contain an edits array.")
    for edit in payload["edits"]:
        if not isinstance(edit, dict) or not isinstance(edit.get("path"), str) or not isinstance(edit.get("content"), str):
            raise ValueError("Each edit must contain a path and complete text content.")
        if len(edit["content"].encode("utf-8")) > MAX_FILE_BYTES:
            raise ValueError("An edit exceeds the per-file size limit.")
    return payload


def _copy_study(root, destination):
    def ignore(current, names):
        omitted = []
        for name in names:
            if os.path.islink(os.path.join(current, name)):
                omitted.append(name)
            elif name in {".git", ".venv", "venv", "__pycache__", "runs", "node_modules", "dist", "build"}:
                omitted.append(name)
            elif name == "store.sqlite3" or name.endswith((".pem", ".key", ".p12", ".pfx")):
                omitted.append(name)
            elif name in {".env", ".env.local", "credentials", "secrets.json"}:
                omitted.append(name)
        return omitted
    shutil.copytree(root, destination, ignore=ignore, symlinks=False)


def _apply_edits(root, edits):
    diffs = []
    real_root = os.path.realpath(root)
    for edit in edits:
        relative = safe_relative_path(edit["path"])
        target = os.path.join(root, relative)
        parent = os.path.realpath(os.path.dirname(target))
        if os.path.commonpath([real_root, parent]) != real_root:
            raise SafetyError("Edit path resolves outside the scratch workspace.")
        if os.path.lexists(target) and (os.path.islink(target) or not os.path.isfile(target)):
            raise SafetyError("Edits may target regular files only.")
        old = ""
        if os.path.exists(target):
            if not is_regular_text_file(target):
                raise SafetyError("Existing target is too large or not a regular file.")
            with open(target, "r", encoding="utf-8") as source:
                old = source.read()
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="") as destination:
            destination.write(edit["content"])
        diff = difflib.unified_diff(old.splitlines(True), edit["content"].splitlines(True),
                                    fromfile="a/" + relative, tofile="b/" + relative)
        diffs.extend(diff)
    return "".join(diffs)


def _run_fixed_tests(root, timeout=30):
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    test_env = os.environ.copy()
    test_env.pop("OPENAI_API_KEY", None)
    try:
        result = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                universal_newlines=True, timeout=timeout, check=False, env=test_env)
        return {"command": command, "exit_code": result.returncode, "output": result.stdout[-12000:], "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", "replace")
        return {"command": command, "exit_code": None, "output": output[-12000:], "timed_out": True}


def _write_json(path, value):
    with open(path, "w", encoding="utf-8") as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write("\n")


def _git_snapshot(root):
    """Return the repository revision and cleanliness, or nulls for non-Git test fixtures."""
    revision = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              universal_newlines=True, check=False)
    if revision.returncode != 0:
        return None, None
    status = subprocess.run(["git", "-C", root, "status", "--porcelain", "--untracked-files=all"],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            universal_newlines=True, check=False)
    if status.returncode != 0:
        return revision.stdout.strip(), None
    return revision.stdout.strip(), not bool(status.stdout.strip())


def run_task(repo_path, task_text, profile_name, provider, output_root, confirm_external=False,
             allow_test_execution=False, memory_text="", timeout=30, defer_test_execution=False):
    if profile_name not in PROFILES:
        raise ValueError("Unknown profile: " + profile_name)
    root = require_study_repo(repo_path)
    target_revision, target_clean = _git_snapshot(root)
    if target_revision is not None and target_clean is not True:
        raise SafetyError("The target Git checkout must be clean before a reproducible run.")
    factory_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    factory_revision, factory_clean = _git_snapshot(factory_root)
    if getattr(provider, "model", "") != "scripted-test-fixture" and not confirm_external:
        raise SafetyError("External model use requires --confirm-external-model.")
    if not isinstance(task_text, str) or not task_text.strip():
        raise ValueError("Task text must not be empty.")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = os.path.abspath(os.path.join(output_root, run_id))
    os.makedirs(run_dir, exist_ok=False)
    started = time.monotonic()
    profile = PROFILES[profile_name]
    if profile["verification"] and not allow_test_execution and not defer_test_execution:
        raise SafetyError("Running repository tests requires --allow-test-execution.")
    if profile["verification"] and allow_test_execution and defer_test_execution:
        raise SafetyError("Choose either --allow-test-execution or --defer-test-execution.")
    entries, selected, context = select_context(root, profile["repository_map"])
    if profile["persistent_memory"] and memory_text:
        context += "\n--- PERSISTENT STUDY MEMORY ---\n" + memory_text
    manifest_digest = hashlib.sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    prompt = SYSTEM_INSTRUCTIONS + "\n\nTASK\n" + task_text.strip() + "\n\nREPOSITORY CONTEXT\n" + context
    response = provider.generate(prompt)
    proposed = _parse_result(response["text"])
    scratch = os.path.join(run_dir, "scratch")
    _copy_study(root, scratch)
    patch_text = _apply_edits(scratch, proposed["edits"])
    with open(os.path.join(run_dir, "patch.diff"), "w", encoding="utf-8") as patch_file:
        patch_file.write(patch_text)
    with open(os.path.join(run_dir, "proposal.json"), "w", encoding="utf-8") as proposal_file:
        json.dump(proposed, proposal_file, indent=2)
        proposal_file.write("\n")

    test_result = None
    if profile["verification"] and allow_test_execution:
        test_result = _run_fixed_tests(scratch, timeout=timeout)
        _write_json(os.path.join(run_dir, "verification.json"), test_result)

    review_result = None
    review_response = None
    review_deferred = bool(profile["review_pass"] and defer_test_execution)
    if profile["review_pass"] and not defer_test_execution:
        review_prompt = (SYSTEM_INSTRUCTIONS + "\n\nReview the proposed patch and verification record. Return JSON with keys "+
                         "summary, findings (array), and verdict (approve|revise|unable_to_assess).\n\nPATCH\n"+
                         patch_text + "\n\nVERIFICATION\n" + json.dumps(test_result))
        review_response = provider.generate(review_prompt)
        review_result = review_response["text"]
        with open(os.path.join(run_dir, "review.txt"), "w", encoding="utf-8") as review_file:
            review_file.write(review_result)

    metadata = {
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "profile": profile_name,
        "capabilities": profile,
        "task": task_text.strip(),
        "target_marker": ".research-scope.json",
        "target_revision": target_revision,
        "target_working_tree_clean": target_clean,
        "factory_revision": factory_revision,
        "factory_working_tree_clean": factory_clean,
        "task_sha256": hashlib.sha256(task_text.strip().encode("utf-8")).hexdigest(),
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "context_files": selected,
        "context_manifest_sha256": manifest_digest,
        "inventory_file_count": len(entries),
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "model": response.get("model"),
        "response_id": response.get("response_id"),
        "provider_usage": response.get("usage"),
        "review_model": None if review_response is None else review_response.get("model"),
        "review_response_id": None if review_response is None else review_response.get("response_id"),
        "review_provider_usage": None if review_response is None else review_response.get("usage"),
        "proposed_file_count": len(proposed["edits"]),
        "test_exit_code": None if test_result is None else test_result["exit_code"],
        "verification_deferred": bool(profile["verification"] and defer_test_execution),
        "review_pass_performed": review_result is not None,
        "review_deferred": review_deferred,
        "elapsed_seconds": round(time.monotonic() - started, 4),
        "human_intervention": {"required": True, "accepted": False, "notes": "Review patch and any model output before transferring changes."},
        "target_modified": False,
    }
    _write_json(os.path.join(run_dir, "metadata.json"), metadata)
    return run_dir, metadata


def run_review(run_dir, verification_path, provider, confirm_external=False):
    """Review a saved proposal and separately produced test record; executes no target code."""
    if getattr(provider, "model", "") != "scripted-test-fixture" and not confirm_external:
        raise SafetyError("External model use requires --confirm-external-model.")
    run_dir = os.path.realpath(run_dir)
    with open(os.path.join(run_dir, "metadata.json"), encoding="utf-8") as source:
        metadata = json.load(source)
    if metadata.get("profile") != "review" or not metadata.get("review_deferred"):
        raise SafetyError("This run is not a review-profile run awaiting review.")
    with open(os.path.join(run_dir, "patch.diff"), encoding="utf-8") as source:
        patch_text = source.read()
    with open(verification_path, encoding="utf-8") as source:
        test_result = json.load(source)
    review_prompt = (SYSTEM_INSTRUCTIONS + "\n\nReview the proposed patch and independent verification record. "
                    "Return JSON with keys summary, findings (array), and verdict (approve|revise|unable_to_assess).\n\nPATCH\n"+
                    patch_text + "\n\nVERIFICATION\n" + json.dumps(test_result))
    started = time.monotonic()
    response = provider.generate(review_prompt)
    with open(os.path.join(run_dir, "review.txt"), "w", encoding="utf-8") as destination:
        destination.write(response["text"])
    metadata["review_pass_performed"] = True
    metadata["review_deferred"] = False
    metadata["review_model"] = response.get("model")
    metadata["review_response_id"] = response.get("response_id")
    metadata["review_provider_usage"] = response.get("usage")
    metadata["review_elapsed_seconds"] = round(time.monotonic() - started, 4)
    metadata["verification_record"] = os.path.basename(verification_path)
    _write_json(os.path.join(run_dir, "metadata.json"), metadata)
    return metadata

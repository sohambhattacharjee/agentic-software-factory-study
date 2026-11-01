import argparse
import json
import os
import sys

from .context import inventory
from .profiles import PROFILES
from .provider import OpenAIResponsesProvider, ProviderError, ScriptedProvider
from .runner import run_task
from .safety import SafetyError, require_study_repo


def _parser():
    parser = argparse.ArgumentParser(prog="study-factory", description="Run the independent synthetic-study factory prototype.")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_parser = sub.add_parser("inspect", help="inventory a marked synthetic study repository")
    inspect_parser.add_argument("--repo", required=True)

    run_parser = sub.add_parser("run", help="propose a patch in a disposable copy of the study repository")
    run_parser.add_argument("--repo", required=True)
    run_parser.add_argument("--task-file", required=True)
    run_parser.add_argument("--profile", choices=sorted(PROFILES), default="baseline")
    run_parser.add_argument("--provider", choices=("openai", "scripted"), default="scripted")
    run_parser.add_argument("--response-file", help="JSON proposal fixture for offline scripted runs")
    run_parser.add_argument("--memory-file", help="human-authored study memory text file")
    run_parser.add_argument("--output-root", default="runs")
    run_parser.add_argument("--confirm-external-model", action="store_true",
                            help="acknowledge sending selected synthetic repository context and task to OpenAI API")
    run_parser.add_argument("--allow-test-execution", action="store_true",
                            help="allow the fixed unittest command to execute against the disposable copy")
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        if args.command == "inspect":
            root = require_study_repo(args.repo)
            result = {"root": root, "study_id": "synthetic-brownfield-agentic", "files": inventory(root)}
            print(json.dumps(result, indent=2))
            return 0

        root = require_study_repo(args.repo)
        with open(args.task_file, encoding="utf-8") as task_file:
            task_text = task_file.read()
        memory = ""
        if args.memory_file:
            memory_path = args.memory_file
        elif PROFILES[args.profile]["persistent_memory"]:
            memory_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "state", "brownfield-agentic-migration.md")
        else:
            memory_path = None
        if memory_path:
            with open(memory_path, encoding="utf-8") as memory_file:
                memory = memory_file.read()
        if args.provider == "openai":
            if not args.confirm_external_model:
                raise SafetyError("OpenAI-backed runs require --confirm-external-model.")
            provider = OpenAIResponsesProvider()
        else:
            if not args.response_file:
                raise ValueError("Scripted runs require --response-file.")
            with open(args.response_file, encoding="utf-8") as response_file:
                provider = ScriptedProvider(json.load(response_file))
        output_root = args.output_root
        if not os.path.isabs(output_root):
            output_root = os.path.join(os.getcwd(), output_root)
        run_dir, metadata = run_task(
            root, task_text, args.profile, provider, output_root,
            confirm_external=args.confirm_external_model,
            allow_test_execution=args.allow_test_execution,
            memory_text=memory,
        )
        print(json.dumps({"run_dir": run_dir, "metadata": metadata}, indent=2))
        return 0
    except (OSError, ValueError, SafetyError, ProviderError) as exc:
        print("study-factory: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

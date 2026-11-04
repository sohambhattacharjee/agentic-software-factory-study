import json
import os
import subprocess
import tempfile
import unittest

from study_factory.provider import ScriptedProvider
from study_factory.runner import run_task
from study_factory.safety import SafetyError, require_study_repo, safe_relative_path
from study_factory.context import inventory


class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.temp.name, "repo")
        self.output = os.path.join(self.temp.name, "runs")
        os.makedirs(os.path.join(self.repo, "tests"))
        with open(os.path.join(self.repo, ".research-scope.json"), "w", encoding="utf-8") as f:
            json.dump({"study_id": "synthetic-brownfield-agentic", "data_classification": "synthetic-only"}, f)
        with open(os.path.join(self.repo, "README.md"), "w", encoding="utf-8") as f:
            f.write("Synthetic test target\n")
        with open(os.path.join(self.repo, "tests", "test_ok.py"), "w", encoding="utf-8") as f:
            f.write("import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n")

    def tearDown(self):
        self.temp.cleanup()

    def test_unmarked_target_is_rejected(self):
        os.remove(os.path.join(self.repo, ".research-scope.json"))
        with self.assertRaises(SafetyError):
            require_study_repo(self.repo)

    def test_run_rejects_dirty_git_target(self):
        subprocess.run(["git", "init", "-q", self.repo], check=True)
        subprocess.run(["git", "-C", self.repo, "add", "-A"], check=True)
        subprocess.run(["git", "-C", self.repo, "-c", "user.name=Study", "-c",
                        "user.email=study@example.invalid", "commit", "-qm", "initial"], check=True)
        with open(os.path.join(self.repo, "README.md"), "a", encoding="utf-8") as f:
            f.write("uncommitted change\n")
        provider = ScriptedProvider({"summary": "no change", "edits": [], "risks": []})
        with self.assertRaises(SafetyError):
            run_task(self.repo, "No change.", "baseline", provider, self.output)

    def test_relative_path_rejects_traversal(self):
        with self.assertRaises(SafetyError):
            safe_relative_path("../outside.txt")

    def test_inventory_excludes_database_files(self):
        with open(os.path.join(self.repo, "study.sqlite3"), "wb") as f:
            f.write(b"not source context")
        paths = [entry["path"] for entry in inventory(self.repo)]
        self.assertNotIn("study.sqlite3", paths)

    def test_run_edits_disposable_copy_and_leaves_target_unchanged(self):
        provider = ScriptedProvider({"summary": "fixture", "edits": [{"path": "README.md", "content": "changed\n"}], "risks": []})
        run_dir, metadata = run_task(self.repo, "Change the README.", "baseline", provider, self.output)
        with open(os.path.join(self.repo, "README.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "Synthetic test target\n")
        with open(os.path.join(run_dir, "scratch", "README.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "changed\n")
        self.assertFalse(metadata["target_modified"])
        self.assertIsNone(metadata["target_revision"])
        self.assertIsNotNone(metadata["factory_revision"])
        self.assertIn("factory_working_tree_clean", metadata)
        self.assertIn("task_sha256", metadata)
        self.assertIsNone(metadata["provider_usage"])
        self.assertTrue(os.path.isfile(os.path.join(run_dir, "patch.diff")))

    def test_verification_profile_requires_explicit_permission(self):
        provider = ScriptedProvider({"summary": "no change", "edits": [], "risks": []})
        with self.assertRaises(SafetyError):
            run_task(self.repo, "No change.", "verification", provider, self.output)

    def test_verification_runs_fixed_tests_in_scratch(self):
        provider = ScriptedProvider({"summary": "no change", "edits": [], "risks": []})
        run_dir, metadata = run_task(self.repo, "No change.", "verification", provider, self.output,
                                     allow_test_execution=True)
        self.assertEqual(metadata["test_exit_code"], 0)
        self.assertTrue(os.path.isfile(os.path.join(run_dir, "verification.json")))

    def test_verification_does_not_pass_api_key_to_test_process(self):
        test_path = os.path.join(self.repo, "tests", "test_no_secret.py")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("import os, unittest\nclass SecretCheck(unittest.TestCase):\n"
                    " def test_api_key_not_inherited(self): self.assertNotIn('OPENAI_API_KEY', os.environ)\n")
        provider = ScriptedProvider({"summary": "no change", "edits": [], "risks": []})
        old_key = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "fixture-only-secret"
        try:
            _, metadata = run_task(self.repo, "No change.", "verification", provider, self.output,
                                   allow_test_execution=True)
        finally:
            if old_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = old_key
        self.assertEqual(metadata["test_exit_code"], 0)

    def test_review_call_usage_is_recorded_separately(self):
        class UsageProvider:
            model = "scripted-test-fixture"

            def __init__(self):
                self.calls = 0

            def generate(self, prompt):
                self.calls += 1
                if self.calls == 1:
                    text = json.dumps({"summary": "no change", "edits": [], "risks": []})
                else:
                    text = json.dumps({"summary": "reviewed", "findings": [], "verdict": "approve"})
                return {"text": text, "model": self.model, "response_id": "fixture-%d" % self.calls,
                        "usage": {"input_tokens": 100 * self.calls, "output_tokens": 10 * self.calls}}

        run_dir, metadata = run_task(self.repo, "No change.", "review", UsageProvider(), self.output,
                                     allow_test_execution=True)
        self.assertEqual(metadata["response_id"], "fixture-1")
        self.assertEqual(metadata["provider_usage"]["input_tokens"], 100)
        self.assertEqual(metadata["review_response_id"], "fixture-2")
        self.assertEqual(metadata["review_provider_usage"]["input_tokens"], 200)
        self.assertTrue(os.path.isfile(os.path.join(run_dir, "review.txt")))

    def test_memory_profile_includes_author_memory(self):
        provider = ScriptedProvider({"summary": "no change", "edits": [], "risks": []})
        run_task(self.repo, "No change.", "memory", provider, self.output, memory_text="STUDY MEMORY NOTE")
        self.assertIn("STUDY MEMORY NOTE", provider.prompts[0])


if __name__ == "__main__":
    unittest.main()

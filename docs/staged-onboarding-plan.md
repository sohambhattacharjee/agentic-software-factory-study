# Staged onboarding plan for the synthetic brownfield application

This plan treats onboarding as a sequence of gated capabilities around an independently created application. It uses only the marked study repository and study-authored artifacts. The original pilot remains frozen; later engineering and evaluation work uses versioned revisions and separate cohorts.

## Stages and completion evidence

| Stage | Capability added | Completion gate | Evidence artifact |
| --- | --- | --- | --- |
| 0. Scope and baseline | Identify the synthetic target and its immutable starting revision. | `.research-scope.json` is present; checkout is clean; baseline tests and seed procedure are recorded. | Target SHA, clean-tree record, baseline test output. |
| 1. Repository discovery | Inventory files and entry points without modifying the target. | Inventory contains only expected study files; a human confirms the scope. | Inventory JSON and file count. |
| 2. Curated context | Supply selected README, requirements, architecture, and fixed task text. | Context file list and hashes are recorded; no external or employer material is included. | Context manifest and prompt/task hashes. |
| 3. Persistent study memory | Add human-authored notes about synthetic behavior and design constraints. | Notes have a source and revision; the researcher reviews them before use. | Memory revision/hash and included-file manifest. |
| 4. Isolated proposal | Ask the model for complete file proposals in a disposable copy. | Proposal stays within the declared text-file boundary; target SHA and working tree are unchanged. | Raw proposal, patch, usage, response ID, and target-integrity fields. |
| 5. Fixed verification | Run preregistered checks against the saved proposal in a separate local process. | Tests are restored from the pinned target, run with a fixed command, and the API key is absent from the test process. | Test output, exit status, timeout, and acceptance/regression counts. |
| 6. Review and human promotion | Send only the saved diff and verification record for a second-pass review. A human decides whether any implementation is accepted. | Review result is saved; reviewer conflicts and coverage gaps are visible; human approval is recorded before transfer. The factory itself does not commit or push. | Review response/usage plus human disposition and, if accepted, a separate reviewed commit. |

## Current status

- The original cancellation cohort covered proposal, fixed verification, and same-model review on an immutable pre-feature revision. It remains a completed exploratory pilot, not evidence that one profile is superior.
- A separate follow-up branch includes a human-authored cancellation implementation, a legacy SQLite schema upgrade, concurrency checks, and handler-level HTTP request tests.
- The order-detail follow-up task completed with 15 proposals (three per profile) against pinned revisions, then three same-model reviews. After a sandbox issue with TCP-bound tests, a documented protocol amendment switched only the test transport to local Unix socket pairs; the saved proposals were re-evaluated without replacement. All 15 passed the three task checks and 11 regression checks. The all-pass result has ceiling effects and does not separate profiles.
- The order-detail implementation was then independently authored on the application follow-up branch and passed all 14 tests. No generated proposal was transferred automatically.
- A second cumulative stage adds express delivery across the legacy order API and shipping service. Fifteen proposals were generated from one pinned revision, then evaluated using a documented test/spec amendment; all fifteen passed the corrected 5 acceptance and 14 regression checks. Three same-model reviews approved without findings. The initial error-body mismatch remains preserved in the app evidence. The independently authored implementation passed all 19 tests.
- A third follow-up stage exercises resilience at the same monolith-to-shipping-service boundary. Its frozen suite checks malformed JSON, response shape, missing or mistyped costs, negative costs, and no order or stock mutation on invalid quotes. The pre-implementation target passed 1 of 7 acceptance checks; 15 proposals (three per profile) passed all 7 acceptance checks and 19 regression tests. Three same-model reviews approved without findings. This separate cohort also reaches a pass ceiling; it does not distinguish profiles. The task, preregistration, scored summary, and raw archive are preserved in the private repositories.

## Practical safeguards

- Use clean, immutable revisions for every scored run; write proposals and evaluations under ignored run directories.
- Do not apply a model proposal automatically. Review the patch, test evidence, and reviewer notes, then record a separate human decision.
- Report same-model reviews as non-independent. Treat a pass at the ceiling as a limitation, and keep follow-up cohorts distinct from the original pilot.
- Keep the repository private during the study. This scope boundary is not a legal determination of IP ownership.

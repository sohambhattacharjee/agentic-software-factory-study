# Experiment protocol draft

This is a preparation document, not a preregistration. Freeze the task, acceptance tests, run count, provider settings, and scoring rules before collecting scored runs.

## Unit of analysis

One fixed engineering task run against an immutable revision of the synthetic brownfield application under one declared factory profile.

## Staged profiles

| Profile | Added capability |
| --- | --- |
| `baseline` | Basic entry-point context only |
| `context` | Repository inventory and selected project documentation |
| `memory` | Human-authored persistent study memory |
| `verification` | Fixed test command against disposable workspace |
| `review` | Separate second-pass review of patch and verification output; same provider by default, so not an independent model |

## Controls to freeze before model-backed evaluation

- Target repository revision and seed-state procedure.
- Exact task wording and acceptance criteria.
- Profile and capability flags.
- Model provider, model identifier, generation settings, and date.
- Run count and ordering across profiles.
- Test command, timeout, and failure interpretation.
- Human-intervention categories and scoring rules.

## Proposed measures

Use one fixed synthetic maintenance task (the cancellation task) and the same immutable target revision for every profile. Each run starts from a fresh copy of that revision. Profiles are cumulative capability bundles, so comparisons estimate the effect of each added bundle in this prototype; they do not isolate individual features.

Primary outcome:

- Task acceptance: number of prewritten acceptance checks passed, plus an all-checks-passed indicator. The cancellation task needs a dedicated acceptance suite before scored runs; the existing five characterization tests alone do not cover cancellation.

Secondary outcomes:

- Regression: fixed characterization suite exit status, test count, failures, and timeout.
- Change size: proposed files and added/deleted lines from the saved diff.
- Process: completed attempts, elapsed time, provider/model identifier, and human interventions (categorized before scoring).
- Safety: whether target revision and working tree remained unchanged, and whether the proposal stayed within allowed text files.
- Review: findings and disposition from the review profile, scored separately from task acceptance because it uses the same provider by default.

Report counts and per-run observations. With one synthetic application and one task, treat the findings as an exploratory case study; do not make broad effectiveness claims from a small number of repetitions.

## Proposed run procedure

1. The fixed cancellation acceptance suite is prepared separately from the preserved baseline snapshot. The pre-implementation target revision is `8ad4aa635e5288b2889814f294c86c861e32341e`; its expected baseline results are recorded in the target repository at `evidence/task-preparation/add-cancellation-2026-11-03.json`. All scored profiles must use this exact revision.
2. Freeze the exact task text, acceptance rubric, fixed test command, model name, API settings, date range, and retry policy.
3. Run five exploratory repetitions per profile, with all five profiles represented in each block and profile order randomized within each block. Every run begins from the same pre-task revision. Label provider failures and invalid outputs as attempts; do not silently replace them.
4. Keep scripted fixture runs separate from scored model runs. Scripted runs validate the runner and evidence format only.
5. Before scored runs, extend evidence capture to include provider usage/token counts when returned by the API. Until then, token usage and cost are unavailable and must not be inferred from elapsed time.

The proposed five repetitions per profile are a pilot choice, not a claim of statistical power. Revisit the run count after a cost check and before starting the scored set.

## Per-run record

Capture run ID, task ID, input revision, profile, context file hashes, prompt hash, provider/model, response IDs where provided, elapsed time, proposed files and diff size, test status/output, acceptance score, review findings, manual edits/interventions, accepted/rejected status, and failures. Record token usage and cost only if supported by captured provider usage and a dated price source. Do not mix demonstration runs with scored runs.

## Interpretation limit

This local prototype is designed to support an independently reproducible synthetic case study. Its outcomes do not establish that the same factory or migration process is safe or effective for employer systems.

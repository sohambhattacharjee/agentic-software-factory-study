# Experiment protocol draft

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

## Per-run record

Capture run ID, task ID, input revision, profile, context file hashes, prompt hash, provider/model, response IDs where provided, elapsed time, proposed files, test status/output, review findings, manual edits, accepted/rejected status, and failures. Do not mix demonstration runs with scored runs.

## Interpretation limit

This local prototype is designed to support an independently reproducible synthetic case study. Its outcomes do not establish that the same factory or migration process is safe or effective for employer systems.

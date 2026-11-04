# Independent Agentic Software Factory Study

An independently built research prototype for staged agentic maintenance of the synthetic order-management application in `brownfield-agentic-migration`. It is not a copy, integration, or reconstruction of any employer system or workflow.

## Research boundary

Use this factory only with the synthetic study repository and other independently created materials. The CLI requires a `.research-scope.json` marker before it reads a target. It does not use work credentials, private prompts, proprietary configurations, or employer code.

Model-backed runs are opt-in. They require an API key in `OPENAI_API_KEY`, a model in `OPENAI_MODEL`, and the explicit `--confirm-external-model` flag because selected repository text and the task prompt will be sent to the OpenAI API. No API request is made during installation or testing. The adapter uses the OpenAI Responses API and sets `store` to `false`; see the [official API reference](https://developers.openai.com/api/reference/resources/responses/methods/create).

## Initial implementation

Python 3.9+; standard library only.

```sh
python3 -m study_factory.cli inspect --repo /path/to/brownfield-agentic-migration
python3 -m study_factory.cli run --repo /path/to/brownfield-agentic-migration \
  --task-file tasks/add-cancellation.md --profile context \
  --provider scripted --response-file examples/cancellation-response.json
```

The initial version supports staged profiles (`baseline`, `context`, `memory`, `verification`, `review`), repository inventory, independently authored persistent memory, isolated scratch execution, fixed test-command execution, patch artifacts, and an optional second-pass review. It never commits, pushes, opens a pull request, or edits the target repository. Outputs remain under ignored `runs/` until a human reviews them.

## Experimental stages

1. Baseline: task prompt and basic source context.
2. Repository context: add file inventory and selected documentation.
3. Persistent memory: add the study's human-authored architecture and behavior notes.
4. Verification: run the repository's fixed characterization suite in an isolated copy.
5. Independent review: ask for a review of the proposed diff and test output.

Each run records its profile, prompt hash, context manifest, model identifier when used, timings, test status, review result, and intervention fields. The factory itself will be improved in small, versioned steps; this initial state is the factory baseline.

The first local runner smoke check is summarized in [`evidence/protocol-smoke-2026-10-31.json`](evidence/protocol-smoke-2026-10-31.json). It used a scripted empty proposal and is not a scored model result.

## Safety and limits

- Runs modify a disposable copy, never the target.
- The factory accepts only the marked synthetic study repo.
- It runs one fixed, non-model-selected test command; model output cannot execute shell commands.
- The verification subprocess does not inherit `OPENAI_API_KEY` from the factory process.
- For model-backed runs, use `--defer-test-execution` and evaluate the saved scratch copy separately. The `review` command sends a saved diff and verification record to the model without executing target code.
- Generated edits are restricted to regular text files inside the scratch copy.
- OpenAI-backed requests transmit the selected task and context to the OpenAI API only after explicit CLI acknowledgement.
- This prototype is an experimental tool, not a production deployment or a legal determination of IP ownership.

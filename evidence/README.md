# Factory baseline evidence

This initial factory implementation is its own baseline. Record the Git revision and environment before changing capability code. Keep generated run directories local because they can contain prompts and repository context; they are ignored by Git.

- Initial implementation state: first independently built prototype at factory revision `32c516e7122d438d05fb0d82d96177243901f8ae`.
- Environment: Python 3.9.6, Darwin 25.6.0 arm64, standard library only.
- Factory characterization suite: 7 tests passed in 0.071 seconds with `python3 -m unittest discover -s tests -v`.
- Scripted protocol run: `20261101T004640591604Z`; target revision `1f80afd25b7e9c6bf6478dc48ba17aceae90d372`; profile `verification`; 0 proposed edits; fixed target test command exited 0; target was not modified. This is a runner check, not a scored model result.
- Fresh factory suite check: [`factory-verification-2026-11-03.json`](factory-verification-2026-11-03.json); 7 tests passed at factory revision `6845c49b8780ee6075ef617e90b3874297769330`.
- A fresh application suite check at the preserved target revision is recorded in the application repository at `evidence/baseline/verification-2026-11-03.json`.
- The cancellation task precondition is recorded at target revision `8ad4aa635e5288b2889814f294c86c861e32341e`. Its five existing characterization checks pass and its three new cancellation acceptance checks fail as expected before implementation; see `evidence/task-preparation/add-cancellation-2026-11-03.json` in the target repository.
- Offline smoke checks ran the scripted fixture through all five profiles at that target revision and the factory revision `b3cca6cb5506b7041b84388ee0d1bec3304a71c1`; the summary is in [`offline-profile-smoke-2026-11-03.json`](offline-profile-smoke-2026-11-03.json), with raw local runs under ignored `runs/protocol-smoke-2026-11-03/`. The two verification profiles exit 1 because the cancellation feature is not implemented. This is pipeline evidence only.
- The initial cancellation cohort, order-detail follow-up, and express-delivery cohort are recorded in the application repository's scored-cohort evidence and raw archive.
- The preregistered shipping-quote resilience cohort completed with 15 proposals (three per profile) and three same-model reviews. All proposals passed 7 acceptance and 19 regression checks; all three reviews approved. See [`scored-cohort-shipping-resilience-2026-11-04.json`](scored-cohort-shipping-resilience-2026-11-04.json). Raw run directories remain ignored locally; the corresponding raw archive is in the private application repository.
- API credentials are retrieved from the user's local Keychain only at runtime; no key is stored in this repository or in run evidence.
- Target application: the independently created synthetic repo marked by `.research-scope.json`.

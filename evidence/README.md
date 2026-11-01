# Factory baseline evidence

This initial factory implementation is its own baseline. Record the Git revision and environment before changing capability code. Keep generated run directories local because they can contain prompts and repository context; they are ignored by Git.

- Initial implementation state: first independently built prototype at factory revision `32c516e7122d438d05fb0d82d96177243901f8ae`.
- Environment: Python 3.9.6, Darwin 25.6.0 arm64, standard library only.
- Factory characterization suite: 7 tests passed in 0.071 seconds with `python3 -m unittest discover -s tests -v`.
- Scripted protocol run: `20261101T004640591604Z`; target revision `1f80afd25b7e9c6bf6478dc48ba17aceae90d372`; profile `verification`; 0 proposed edits; fixed target test command exited 0; target was not modified. This is a runner check, not a scored model result.
- Model-backed experiment: not run; no API key is stored or transmitted by this repository.
- Target application: the independently created synthetic repo marked by `.research-scope.json`.

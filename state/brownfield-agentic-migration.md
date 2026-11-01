# Synthetic study memory

- The target is a fictional Python 3.9+ order and inventory API using SQLite.
- `app/legacy_monolith.py` contains route handling, validation, order rules, SQL, and the shipping HTTP client in one module.
- `app/shipping_service.py` is a separate local HTTP service that returns deterministic shipping quotes.
- Run target characterization checks with `python3 -m unittest discover -s tests -v`.
- Sample records and business rules are synthetic and must remain separate from employer materials.
- Preserve the captured baseline under `evidence/baseline/`; append experimental outputs under new stage directories.

# Task: add an express delivery option across the order and shipping services

Add an optional `delivery_speed` value to the synthetic order workflow and carry it through the legacy order API to the newer shipping-quote service.

Acceptance criteria:

1. Order requests may omit `delivery_speed`; omission means `standard`, and existing standard shipping prices and the existing standard order-response shape remain unchanged. The monolith sends `delivery_speed: "standard"` to the shipping service.
2. `delivery_speed: "express"` is forwarded to the shipping service. Express shipping costs exactly 800 cents more than the existing standard quote for the same city and subtotal. The order persists and returns the express speed, and the order listing exposes that speed for express orders.
3. Unsupported speeds return HTTP 400 with `{\"error\":\"invalid_delivery_speed\"}` before a shipping request, order write, or stock decrement.
4. The shipping service quote function and `/quote` endpoint accept standard by default and express explicitly; the standard quote representation and rate remain unchanged. Invalid speed is rejected by the service with HTTP 400.
5. Existing seeded orders in a pre-speed database remain readable as standard orders after initialization; the migration is safe to run more than once.
6. Existing cancellation, order detail, product, order-list, order-creation, health, and characterization behavior remains intact.

The target repository contains fixed acceptance tests in `tests/test_delivery_speed_acceptance.py` alongside the fixed existing suites. Use the full test suite.

Return a JSON proposal with only complete file contents for files that must change. Do not execute commands or modify the target directly.

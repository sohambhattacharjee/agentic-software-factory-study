# Task: add an order detail endpoint

Add a read-only HTTP endpoint for retrieving one order by numeric ID.

Acceptance criteria:

1. `GET /api/orders/{id}` returns HTTP 200 with the same JSON representation as that order in `GET /api/orders`, including its items and any non-active status already exposed by the list endpoint.
2. A well-formed numeric ID that does not exist returns HTTP 404 with `{\"error\":\"order_not_found\"}`.
3. A malformed ID returns HTTP 400 with `{\"error\":\"invalid_order_id\"}`.
4. The request does not modify orders, items, or product stock.
5. Existing product, order-list, order-creation, health, and cancellation behavior remains unchanged.

The target repository contains fixed acceptance tests in `tests/test_order_detail_acceptance.py`, alongside the fixed characterization and cancellation suites. Use the full test suite.

Return a JSON proposal with only complete file contents for files that must change. Do not execute commands or modify the target directly.

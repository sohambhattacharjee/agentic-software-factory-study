# Task: add order cancellation with inventory restoration

Implement order cancellation in the existing HTTP API.

Acceptance criteria:

1. `DELETE /api/orders/{id}` cancels the order identified by its numeric ID and returns HTTP 200 with `{"status":"canceled"}`.
2. A successful cancellation marks the listed order as canceled and restores every item's quantity to product stock exactly once.
3. Canceling an unknown order returns HTTP 404 with `{"error":"order_not_found"}`.
4. Repeating cancellation returns HTTP 409 with `{"error":"already_canceled"}` and does not restore stock again.
5. Existing order creation and listing behavior remains unchanged.

The target repository contains a fixed acceptance suite in `tests/test_cancellation_acceptance.py`. Use it together with the existing characterization suite.

Return a JSON proposal with only complete file contents for files that must change. Do not execute commands or modify the target directly.

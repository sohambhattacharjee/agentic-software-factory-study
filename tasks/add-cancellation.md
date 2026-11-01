# Task: add order cancellation with inventory restoration

Implement a cancellation operation for an existing order.

Acceptance criteria:

1. A caller can cancel an order by its numeric ID.
2. A successful cancellation marks the order canceled and restores every item's quantity to product stock exactly once.
3. Canceling an unknown order returns a clear not-found response.
4. Repeating cancellation does not restore stock twice.
5. Existing order creation and listing behavior remains unchanged.

Return a JSON proposal with only complete file contents for files that must change. Do not execute commands or modify the target directly.

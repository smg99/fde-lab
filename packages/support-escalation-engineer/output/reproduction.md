# Reproduction

Result: **REPRODUCIBLE**

## Steps
1. Send POST to POST /api/v1/checkout with payload: {"cart_id": "cart_9921", "discount_code": "SAVE20", "payment_method": "credit_card"}

## Expected
Checkout completes with HTTP 200.

## Observed
Checkout fails with HTTP 500. Matches reported issue.

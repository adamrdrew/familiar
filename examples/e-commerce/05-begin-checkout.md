# Begin Checkout Process

Click the "Checkout" or "Proceed to Checkout" button

Wait for the checkout page or process to begin

The checkout flow might ask for:
- Login/registration (if we haven't logged in yet)
- Shipping address
- Billing information
- Payment method

For this test, we'll proceed until we reach a form asking for information.

If login is required:
- Enter email: ${TEST_USER}
- Enter password: ${TEST_PASSWORD}
- Click login/continue

## Expected Outcome

Checkout process begins, possibly showing login form or address form.
We should progress to the point where payment/shipping information is requested.

**Note**: This test does NOT complete the actual purchase - we stop before final submission.


# E-Commerce Purchase Flow Example

This example demonstrates a complete e-commerce user journey with Familiar.

## Overview

This test suite verifies a full shopping experience:
1. Visit homepage
2. Search for a product
3. View product details
4. Add product to cart
5. View shopping cart
6. Begin checkout
7. Verify checkout form

**Note**: This test intentionally stops before final purchase to avoid creating real orders.

## Prerequisites

- An e-commerce website or demo site
- (Optional) Test user account if login is required

## Setup

### 1. Set Environment Variables

```bash
# Application URL
export BASE_URL="https://your-store.com"

# Optional: Test account if login required
export TEST_USER="test@example.com"
export TEST_PASSWORD="testpass123"

# LLM Configuration
export FAMILIAR_MODEL_PROVIDER="anthropic"
export FAMILIAR_MODEL="claude-3-5-sonnet-20241022"
export ANTHROPIC_API_KEY="your-api-key"
```

### 2. Run the Test

```bash
familiar run examples/e-commerce

# With detailed logging
familiar run examples/e-commerce --verbose

# Watch the browser
familiar run examples/e-commerce --no-headless
```

## Example Output

```
╭─────────────────────────────────────────────────────╮
│ ✓ E-Commerce Purchase Flow              PASSED     │
╰─────────────────────────────────────────────────────╯

┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Status ┃ Step                          ┃ Duration ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ ✓ PASS │ Visit Homepage and Verify     │   3.2s   │
│ ✓ PASS │ Search for Product            │   4.5s   │
│ ✓ PASS │ Select a Product              │   5.1s   │
│ ✓ PASS │ Add Product to Shopping Cart  │   3.8s   │
│ ✓ PASS │ View Shopping Cart            │   2.9s   │
│ ✓ PASS │ Begin Checkout Process        │   6.2s   │
│ ✓ PASS │ Verify Checkout Form          │   2.4s   │
└────────┴───────────────────────────────┴──────────┘

Suite completed in 28.1s - All tests passed!
```

## Configuration Details

### Retry Policy

This suite uses exponential backoff to handle:
- Slow page loads
- API rate limiting
- Network variability

```yaml
retry_policy:
  type: "exponential"
  max_retries: 3
  base_delay: 2.0
  max_delay: 30.0
```

### Fuzziness

Allows 15% of steps to fail, which is useful for non-critical elements:

```yaml
fuzziness: 0.15
```

With 7 steps, 1 step can fail and the suite still passes.

## Customization

### Test Different Products

Change the product search term:

```bash
export PRODUCT_SEARCH="running shoes"
```

Or edit `suite.yaml`:

```yaml
env:
  PRODUCT_SEARCH: "wireless headphones"
```

### Add More Validation

Create additional steps:
- `07-verify-shipping-options.md`
- `08-apply-discount-code.md`

### Complete the Purchase (Carefully!)

If you want to test actual purchase completion:

1. Use a test/sandbox environment
2. Add step `07-complete-purchase.md`
3. Ensure you have test payment methods configured

**⚠️ Warning**: Only do this in safe test environments!

## Troubleshooting

**Search fails to find products:**
- Check PRODUCT_SEARCH matches available inventory
- Increase step_timeout for slow searches

**Add to cart doesn't work:**
- Some sites require size/color selection first
- Add those interactions to `03-add-to-cart.md`

**Checkout requires login:**
- Ensure TEST_USER and TEST_PASSWORD are set
- Or create an account first

## Testing Variations

### Guest Checkout Flow

Test without login by commenting out login steps or not providing credentials.

### Multiple Products

Modify steps to add multiple items to cart before checkout.

### Promo Codes

Add a step to enter and verify discount codes.

## Demo Sites for Testing

Try this example with these demo e-commerce sites:
- https://demo.vercel.store/
- https://react-shopping-cart-67954.firebaseapp.com/
- Your own staging environment

## Related Examples

- [Basic Login](../basic-login/) - Simple authentication flow
- [API Testing](../api-testing/) - Testing with API calls


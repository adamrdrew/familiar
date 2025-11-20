# E-Commerce Test Context

This test validates a complete e-commerce shopping flow from homepage to checkout.

## Application Structure
- Homepage has product search prominently displayed
- Product listings show in grid or list format
- Each product has "Add to Cart" button
- Cart icon in header shows item count
- Checkout is multi-step process

## Search & Navigation
- Search is performed via search bar in header
- Results appear on new page or dynamically
- Product names and images are clickable
- Breadcrumb navigation helps track location

## Cart & Checkout
- Cart can be accessed from header icon
- Cart shows: item name, quantity, price, subtotal
- Checkout button leads to checkout form
- Form typically asks for: shipping, billing, payment info
- Confirmation page shows order number and summary

## Common UI Patterns
- Loading spinners during search and page transitions
- "Continue Shopping" links back to products
- Quantity can be adjusted in cart (+ / - buttons)
- Total price updates dynamically
- Form validation provides immediate feedback

## Known Quirks
- Sometimes search results take 1-2 seconds to load
- Cart totals may update with slight delay
- Checkout form validation happens on blur (after leaving field)
- Success pages often have delay before showing confirmation

## Test Data
- Search for common items (e.g., "shoes", "laptop", "book")
- Use test payment info (if payment is part of test)
- Shipping address should be complete and valid


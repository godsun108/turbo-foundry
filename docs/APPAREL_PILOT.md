# Apparel pilot — revenue-first launch

Status: **proposal / not yet listed**. No live Printful connection, product price, payment collection, or sale has been verified.

## Goal
Test demand for three original text-led garments with no inventory purchase or paid advertising initially. Reuse existing commerce and reporting infrastructure, but do not confuse a GitHub registry with proof of integration.

## First three concepts
| ID | Exact slogan | Direction | First garment |
| --- | --- | --- | --- |
| ranch-001 | I LOVE RANCH | Bold, absurd, vintage diner typography | Unisex T-shirt |
| goodguy-001 | GOOD GUY. MOMS LOVE ME. | Playful retro varsity lettering | Unisex T-shirt (jacket later) |
| famous-001 | I'M NOT FAMOUS ANYMORE | Minimal understated typography | Unisex T-shirt |

## Gate before public listing
- [ ] Confirm Printful store and integration via authenticated account; never put tokens in repo.
- [ ] Inspect existing products to avoid duplicating listings.
- [ ] Confirm print area, garment, color, sizes, fulfillment location, shipping rates, and taxes.
- [ ] Produce original print-ready artwork; inspect spelling, resolution, transparency, contrast and placement.
- [ ] Check names/slogans and artwork for trademark and rights issues.
- [ ] Calculate contribution margin per SKU: sale price - fulfillment - shipping subsidy - transaction/platform fees - returns allowance.
- [ ] Confirm checkout can accept a real payment and order can reach fulfillment; use a non-chargeable test when supported.
- [ ] Approve public release and any costs explicitly.

## Demand test
Launch only three designs. Use organic content with distinct product links and UTM attribution. Track visitors, add-to-cart, checkouts, paid orders, returns, fulfillment failures and contribution margin. Never claim sales without payment evidence. Compare after sufficient exposure, not arbitrary calendar days.

## Architecture
One parent commerce operation; one experimental apparel storefront with collections. Separate brand identities only after proof of demand. Printful is a supplier, not a customer-acquisition engine. Command Center should read trustworthy payment events; no live payment secrets in GitHub.

## Next action
Obtain authenticated Printful account/store visibility and live product catalog; inspect Stripe/storefront checkout, then prepare art and costed SKU sheet.

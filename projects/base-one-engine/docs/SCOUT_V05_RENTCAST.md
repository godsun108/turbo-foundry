# Scout v0.5 — RentCast Integration

RentCast is the first active-listing provider integrated that does not depend on the Base One operator having an MLS broker relationship.

Official documentation says its sale-listing endpoint searches active/inactive for-sale inventory by city/state, ZIP, address, or geographic area and returns listed price, status, listing dates/contacts and property attributes. RentCast states listing data is sourced from public sources/feeds rather than directly from MLS and is updated at least daily.

## Activate

1. Create a RentCast API account/subscription and generate an API key.
2. Add the key to this repository as GitHub Secret `RENTCAST_API_KEY`.
3. Manually run **Base One Scout - RentCast** once.
4. Inspect the artifact and field mappings before relying on scheduled runs.

No API key belongs in source control.

Target cities are currently Port St. Lucie / Port Saint Lucie, Jensen Beach and Stuart, Florida.

Official docs:
- https://developers.rentcast.io/reference/property-listings
- https://developers.rentcast.io/reference/sale-listings
- https://www.rentcast.io/terms-api

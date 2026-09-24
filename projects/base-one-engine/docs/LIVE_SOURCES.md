# Live Sources

## St. Lucie County Property Appraiser — connected in v0.3

Base One can query the county's public ArcGIS parcel service and normalize selected parcel facts.

This source includes fields such as parcel/property IDs, land-use description, year built, beds, baths, site address, historical sale information, zoning, and appraised/assessed/taxable values.

### Critical semantic rule

**Appraised value is not asking price. Historical sale price is not asking price.**

The v0.3 adapter labels normalized records as `st_lucie_property_appraiser_reference`. Its reference value must not be represented in reports as a current listing price.

This adapter is therefore useful for public-record discovery/enrichment and future cross-checking. A separate permitted active-listing feed is still required for autonomous current-for-sale discovery.

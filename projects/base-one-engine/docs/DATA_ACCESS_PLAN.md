# Base One Scout — Treasure Coast Live Data Access Plan

Research date: 2026-09-24.

## Confirmed paths

### Martin County REALTORS of the Treasure Coast (MCRTC)
MCRTC states that it uses Cotality/CoreLogic Trestle for data-feed authorization and offers RESO-certified Web API feeds. IDX, VOW, and Broker Back-Office requests are initiated by a vendor through Trestle and require the applicable participant/broker contract.

Official page: https://martincountyrealtors.org/data-feeds/

### BeachesMLS
BeachesMLS documents two broker/agent feed paths: FBS/Spark Datamart WebAPI and Cotality Trestle, subject to BeachesMLS approval and licensing. This is a plausible path for coverage relevant to the broader southeast Florida market.

Official broker guidance: https://beachesmls.zendesk.com/hc/en-us/articles/42465806359444-How-Do-I-Apply-for-BeachesMLS-IDX-Access-as-a-Broker

### RESO
RESO defines the Web API standard but explicitly does not supply MLS data. Credentials are issued through the local MLS/provider after licensing/authorization.

Official reference: https://www.reso.org/reso-web-api/

## Recommended integration order

1. MCRTC via Trestle for Martin County/Treasure Coast coverage.
2. Determine the MLS/feed that supplies the desired St. Lucie inventory and obtain its authorized Web API access; BeachesMLS/FBS or Trestle is a documented candidate path where coverage/licensing applies.
3. Store endpoint/token only as GitHub repository secrets.
4. Run metadata/schema probe before enabling daily production discovery.
5. Preserve county Property Appraiser data as independent enrichment/cross-check data.

## Activation checklist

- [ ] Identify eligible MLS participant/broker/data license.
- [ ] Create vendor/developer account with provider.
- [ ] Request appropriate data use (IDX, VOW, broker back-office, or other authorized use).
- [ ] Obtain MLS/provider approval.
- [ ] Receive Web API endpoint and credentials.
- [ ] Add RESO_ENDPOINT and RESO_TOKEN as GitHub Secrets.
- [ ] Run manual Scout Live workflow.
- [ ] Validate fields/status semantics against provider metadata.
- [ ] Enable/retain daily scheduled production runs.

Do not substitute scraped consumer-portal pages for an authorized feed.

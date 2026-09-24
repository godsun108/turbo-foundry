# Base One Scout v0.1

Status: EXPERIMENTAL / RELEASED CORE

Scout is the discovery layer in front of Base One.

**Source adapter → candidates → explicit filters → intake → underwriting → stress test → report → watch for changes**

## Two entry paths

1. **Scout discovery:** permitted data sources produce candidates automatically.
2. **Direct intake:** a property we already like can be inserted into the same pipeline without waiting for Scout to discover it.

## Source policy

Scout is source-agnostic. Adapters should use official/permitted APIs, licensed feeds, user-provided exports, or public records. The core does not depend on unauthorized scraping.

## v0.1 capabilities

- deterministic candidate model
- location/price/type/bed/size filters
- stable ordering
- listing change detection
- manual JSON adapter
- configuration schema

The next release connects one or more live permitted/public sources and persists watch-state between scheduled runs.

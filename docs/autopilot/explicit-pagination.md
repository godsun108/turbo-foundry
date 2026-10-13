# Explicit paged child-call adapter

`enumerate_pages` is an offline, read-only cursor-driven adapter. Its injected `fetch_page` must return `(items, next_cursor)` with `next_cursor=None` **only when the provider has explicitly exhausted all pages**. It bounds pages, legs, and page size, detects cursor loops and duplicates, and fails closed on timeouts and malformed responses.

The adapter is not yet wired to Twilio's concrete page API. `explicit_page_exhaustion` is valid only when the provider-specific implementation guarantees the sentinel semantics. It does not establish eventual consistency, answer state, or messaging eligibility. Retry/backoff, provider authentication and API-specific pagination integration remain pending. No live traffic or SMS is enabled.

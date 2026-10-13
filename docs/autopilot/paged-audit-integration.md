# Explicit paginated provider audit integration

`audit_parent_call` accepts an optional injected `fetch_page(parent_sid,cursor,page_size)` callable. When provided, it uses `enumerate_pages` to obtain explicit cursor exhaustion evidence and compares the enumerated child SIDs against local signed callback records. Timeouts and malformed pages fail closed.

This is **not yet a concrete Twilio pagination adapter**: the injected callable must enforce Twilio API semantics, authenticated account binding, and trustworthy next-page tokens. Even with explicit exhaustion and matching records, the audit still returns `consistent=False` because complete human-answer evidence and eventual consistency are not established. No live SMS or billing.

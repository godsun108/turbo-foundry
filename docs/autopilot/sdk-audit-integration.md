# SDK-managed pagination in provider audit

`audit_parent_call` now accepts an injected `sdk_pager` and calls its bounded `enumerate_all(parent_sid)` method. The retrieved child IDs are compared against signed callback journal records. Pagination errors and account mismatches block reconciliation. A successful match still returns `consistent=False` because provider answer evidence and record-settlement windows remain unverified.

The adapter currently uses injected SDK-shaped test doubles. Before production use, verify actual Twilio SDK page methods and account authentication, implement bounded transient-failure handling, and test delayed child records. No live SMS or billing is enabled.

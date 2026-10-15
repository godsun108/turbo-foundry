# Read-only provider call-history audit

`audit_parent_call` compares local signed callback histories against injected authenticated provider REST call snapshots. It rejects missing local history, mismatched parent status, mismatched child parent links, and child legs that may have answered.

**Critical boundary:** fetching each *known* child leg does not prove that all child legs have been discovered. Therefore even matching records return `provider_leg_completeness_unverified` and `consistent=False`. This audit cannot authorize SMS. Future work needs complete provider-side child enumeration, pagination safeguards, and trustworthy answer-state evidence.

Tests use offline provider fixtures. No real Twilio requests, messages, or billing.

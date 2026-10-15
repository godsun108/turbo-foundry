# Bounded Twilio child-call enumeration

`enumerate_child_calls` requests up to `max_legs + 1` child calls from an injected authenticated Twilio REST client. It rejects oversized responses, malformed SIDs, duplicate child SIDs, and mismatched parent relationships. The result is read-only and cannot send SMS.

**Caution:** The `complete` flag currently means only that the SDK returned a bounded list without an obvious truncation signal. It is **not** proof that all historical legs have been discovered: provider pagination semantics, eventual consistency, and delayed records require independent verification. Do not promote this result to authoritative answer-history evidence or trigger messaging. A follow-up sprint should integrate enumeration with provider audit while preserving fail-closed eligibility.

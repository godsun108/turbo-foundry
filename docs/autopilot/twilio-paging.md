# Twilio SDK pagination adapter (first phase)

`TwilioCallPager` reads the first SDK `calls.page(...)` page with injected authenticated credentials and verifies each child leg's `account_sid` and `parent_call_sid`. It rejects any supplied continuation cursor and fails closed if Twilio advertises a next page. This avoids following arbitrary URLs or treating a truncated response as complete.

**Not finished:** Twilio SDK page API behavior and exact return shapes require integration testing; safe SDK-managed continuation, bounded retries/backoff, timeout handling, and rate-limit handling are still outstanding. Only a single page with no next-page marker can be returned by this adapter. Even then, eventual consistency and definitive answer-state evidence remain unresolved. No production webhook or SMS is enabled.

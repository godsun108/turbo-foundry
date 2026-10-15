# Provider transient-failure handling

The read-only Twilio pager classifies HTTP 429 as `provider_rate_limited`, 500/502/503/504 as `provider_temporarily_unavailable`, and 401/403 as `provider_auth_failed`. Timeouts remain `provider_timeout`. All of these return incomplete results, blocking audit success and downstream messaging authorization.

There are **no automatic retries yet**: retry budgets, Retry-After handling, and asynchronous backoff need an independently tested scheduler. The caller must not interpret an incomplete result as a missed call. A settlement window for delayed provider records remains pending. No live SMS or billing is enabled.

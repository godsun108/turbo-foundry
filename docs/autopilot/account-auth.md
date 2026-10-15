# Trusted Twilio account token lookup

`TrustedAccountVerifier` selects a configured auth token by the callback's claimed `AccountSid`, then validates the signature using that token. An unknown account cannot select an arbitrary secret. Callback fields such as `AuthToken` are never used as credentials.

This is an offline library component; deployment must source secrets from a secure store, reconstruct the exact public webhook URL, handle token rotation, and prevent credential leakage in logs. The account verifier is not yet integrated into the atomic ingest endpoint. Unit tests use injected validators; production must use the official Twilio `RequestValidator`.

No real customer traffic or SMS is enabled.

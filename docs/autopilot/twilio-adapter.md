# Twilio adapter (authentication boundary only)

The module `src/autopilot/twilio_adapter.py` uses Twilio's official Python
`RequestValidator` when invoked without a test validator. Install `twilio`
in the deployment environment. Never commit the auth token.

Pass the exact HTTPS webhook URL and all form parameters as received; do not
normalize the URL or discard unknown parameters before signature verification.
A trusted reverse-proxy configuration is required to reconstruct the externally
requested URL. Reject invalid signatures.

Tests use an injected stub validator: they verify integration flow and
fail-closed behavior, **not** cryptographic interoperability with Twilio.
Before release, add real SDK-generated signature vectors and sandbox testing.

Twilio `CallStatus=completed` is NOT evidence of a missed call. Determining
missed-call eligibility requires a verified call-state model or authoritative
call outcome. This adapter intentionally does not trigger recovery messages.

Twilio legacy test credentials simulate REST API calls but do not produce
real call/message status callbacks. Do not claim a full webhook end-to-end test
based on test credentials alone.

References:
- https://www.twilio.com/docs/usage/webhooks/webhooks-security
- https://www.twilio.com/docs/usage/tutorials/how-to-secure-your-flask-app-by-validating-incoming-twilio-requests
- https://www.twilio.com/docs/iam/test-credentials

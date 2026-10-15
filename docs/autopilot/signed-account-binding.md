# Signed callback account binding

Atomic ingest now requires `AccountSid` in the signature-validated Twilio form fields. It rejects missing or malformed IDs, rejects mismatches with a separately supplied expected account, and checks the signed ID against the registered number/account/tenant tuple for parent calls.

**Limitations:** This requires the correct Twilio account auth token to be selected before signature validation. A production server must use a trusted account-to-token resolver, never select an arbitrary token from untrusted callback fields. Signed callbacks still do not prove complete child-call histories. The test validator is a fixture, not a cryptographic validation test. No live messaging is enabled.

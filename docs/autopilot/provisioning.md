# Number provisioning registry (offline)

`NumberProvisioning` maps a provisioned E.164-like phone number to one
tenant and one provider account SID. It rejects conflicting ownership,
supports explicit disable, and verifies tenant/account/number together.

**Important:** the `provision` and `disable` methods are trusted
administrative fixtures, not public API endpoints. They do not check
ownership against Twilio, authenticate an administrator, or verify the
provider account's rights to a phone number. A real deployment must
authenticate provisioning requests and reconcile ownership against Twilio.

This registry is **not yet wired into `AtomicCallIngest`**. Until it is,
atomic ingest still accepts caller-supplied tenant/number claims. Next work
must make verified registry lookup mandatory for parent events, and ensure
the authenticated provider AccountSid is bound to the configured account.

No real phone number is provisioned and no SMS is sent.

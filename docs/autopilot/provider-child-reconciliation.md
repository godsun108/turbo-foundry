# Provider child-leg reconciliation

The read-only provider audit now enumerates child legs through the bounded Twilio SDK adapter and compares provider-discovered SIDs against local signed callback journal SIDs. Missing provider or local legs fail closed with explicit reasons. Malformed or oversized enumerations fail closed as well.

A matching set is **not** a sufficient basis to send SMS: Twilio pagination semantics, eventual consistency, and the absence of definitive human-answer evidence still prevent authorization. Audit results remain `consistent=False` even when all currently observed records match. No live provider access or outbound messaging is enabled.

# Foundry Mail — private branded email architecture (proposal)

**Status: design only. No Foundry-owned email domain, MX, SMTP server, mailbox, or delivery is verified from this repository. Do not claim the mail system exists, send emails, or publish DNS records based on this document.**

## Mission

Build a private-by-design, iPhone-usable branded email workspace for Foundry and ultimately its clients: human correspondence, permission-based business workflows, shared inboxes, triage assistants, secure audit and export. A custom email UI is realistic; reliable independent SMTP/IMAP infrastructure requires careful operations. “Better than every provider” is an aspiration, not a verified security or deliverability claim.

## Build-versus-buy sequence

**Phase 0 — own identity, do not reinvent mail transport.** Confirm an owned domain and domain/DNS administrator. Create aliases such as hello@<owned-domain>, sales@<owned-domain>, support@<owned-domain> using a reputable hosted or managed mail provider first. Set MX, SPF, DKIM, DMARC, forward/reverse DNS expectations as applicable, TLS, recovery MFA, administrative security and monitored abuse/postmaster inboxes. Do not guess DNS records: use actual provider-generated values. Establish a real and valid postal contact address before commercial outreach, plus opt-out workflow. Test inbound/outbound deliverability manually across providers, reply threading, bounce behavior and account recovery.

**Phase 1 — own application, managed delivery.** Develop a privacy-oriented mobile web inbox/CRM that integrates a provider through delegated permissions. Require per-tenant ACLs, MFA, scoped tokens and refresh/revocation, encryption at rest, provider webhook signature validation, domain isolation, no plaintext body in logs, minimal retention and export/delete controls. Store customer message contents only with explicit permission, a documented basis and approved security boundaries. An AI assistant may summarize or prepare drafts with explicit human approval; default to no autonomous sends.

**Phase 2 — optional own mail transport.** Only after proving account security, staffing and backup/recovery: evaluate self-hosting SMTP, IMAP/JMAP, queue and retry, spam filtering, malware scanning, DKIM key rotation, SPF/DMARC alignment, MTA-STS/TLS-RPT, DNSSEC, authoritative DNS, reverse DNS/PTR, IP reputation and deliverability monitoring, backups/restore and abuse operations. Consider separately managed outbound relay; a functioning mail server does not guarantee inbox delivery. This is a distinct high-risk service, not a prerequisite for first revenue.

**Phase 3 — future improvements.** Human-readable permissions, E2EE where both endpoints support it, passkeys/MFA, signed audit events, transparent AI assistant decisions, protected private search, on-device encrypted caches, iPhone-first operator console, accessibility and export. Do not promise universal end-to-end encryption: ordinary SMTP messages crossing external providers generally cannot offer it by default.

## Foundry mail services to separate

- **Human sales communications:** individually reviewed and sent by a real person; provide accurate sender identity, valid physical postal address, easy opt-out and honor suppression. Never send bulk automated outreach without legal, deliverability and provider policy review.
- **Customer lifecycle/transactional notices:** separate stream, domain/subdomain, provider permission and unsubscribe classification as appropriate; never smuggle marketing into transactions.
- **Customer automation:** tenant-scoped API permissions, consent and human approval boundaries. Never reuse Foundry prospect consent as permission to send a customer's SMS or email.

## Launch checklist

- [ ] Domain ownership and DNS control verified.
- [ ] Appropriate business email service selected, recovery/MFA configured and tested.
- [ ] Real MX/SPF/DKIM/DMARC verified with receiving providers; required PTR/TLS assessed.
- [ ] Inbox and sent-mail retention, backup/export and incident ownership documented.
- [ ] Valid business postal address in commercial messages and clear unsubscribe handling.
- [ ] Approved and tested one-to-one sending and reply tracking; no unapproved auto-send.
- [ ] Privacy and secret threat model signed off before connecting AI/CRM or real customer data.
- [ ] Actual outbound messages and receipts measured; no fictional deliverability metrics.
- [ ] Human operator available to respond and honor opt-outs.

## Standards/resources

- Google official Email sender guidelines: https://support.google.com/mail/answer/81126
- FTC CAN-SPAM business compliance guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Protocols/controls to evaluate: SMTP (RFC 5321), RFC 5322, SPF (RFC 7208), DKIM (RFC 6376), DMARC (RFC 7489), TLS, MTA-STS and TLS reporting.

**Recommendation:** sell a narrow validated automation product first using an authenticated, managed domain mailbox. Build the custom Foundry Mail interface in parallel; defer self-hosting mail transport until revenue and operations justify it. No single hosted provider or bespoke system can guarantee zero access to data, zero outages or perfect deliverability.

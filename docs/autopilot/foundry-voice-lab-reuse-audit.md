# Foundry Voice Lab — reuse audit and integration contract (offline v0)

Status: **design/rehearsal only**. No live phone answering, provider connection, model endpoint, booking, customer recording or deployment is authorized.

## Verified existing source

- PORTAL: `godsun108/The-portal/genesis-voice/index.html` contains browser `SpeechRecognition` / `webkitSpeechRecognition`, `speechSynthesis`, manual Speak/Send/Stop buttons, localStorage text history, 20-second abort on model POST, and checks for `schema=portal.chat.v1`, `verified=true`, assistant role, nonempty response.
- It reads `../intelligence/config.json` for an HTTPS model endpoint; absent configuration it cannot produce model replies. Browser/device speech recognition can involve an external speech provider.
- VHE `godsun108/virtual-human-engine/README.md` describes fictional-character continuity, approval, and provider adapters; the README does not establish a production-grade real-time voice service.
- Foundry `src/autopilot/offline_customer_experience.py` provides deterministic intent triage, urgent/human escalation, simulated STOP, and truthful non-booking responses; it is not an LLM or audio interface.

## Proposed interface boundaries

`SpeechInput.listen() -> {transcript, confidence?, locale, source:'browser'}`
- Require an explicit microphone action and visible listening state; refuse silently recording.
- Speech recognition availability varies by browser, including iPhone Safari. Do not claim local-only processing.

`Conversation.respond({tenant, session, industry, transcript, verified_facts}) -> {text, intent, disposition, verified_booking:false, real_message_sent:false}`
- Use a strict tenant-scoped, approved business-fact catalog. Treat speech transcription as untrusted input.
- Avoid presenting simulated handoff as completed; urgency should fail safely and recommend real emergency channels where appropriate.
- Cap input/output length, context size, and time; support human escalation and opt-out.

`SpeechOutput.speak({text, locale, voice_id?}) -> {started, finished, error?}`
- Browser speechSynthesis is an initial zero-new-spend adapter, **not** a guarantee of human-like speech.
- Stop/cancel speech on explicit interruption. Full duplex/barge-in, streaming ASR/TTS, voice selection and latency remain unimplemented.

`CallAdapter` is **not implemented**; phone numbers, Twilio/SIP, real voicemail, consent compliance, recording policies, and telecom charges require separate review and authorization.

## Acceptance criteria for a future browser demo

1. iPhone browser can initiate a microphone request and see whether speech recognition is supported.
2. Text fallback always works; no credential or token appears in static client code.
3. Simulated receptionist explicitly identifies itself as an AI assistant and does not impersonate a person.
4. Quotes, appointments and handoffs are never confirmed without an authoritative integration receipt.
5. STOP, urgent safety phrases, no microphone permission, timeout and unsupported browser fail visibly.
6. Tenant isolation, safe facts, and no actual customer data; no audio storage without separate informed consent.
7. Instrument response latency, recognition errors, interruption recovery and human-rated naturalness before any live pilot.
8. All demos remain synthetic, isolated from PORTAL model credentials and production resources.

## Build order

1. Browser demo with speechSynthesis + text entry and clearly labeled fictional responses.
2. Optional browser speech recognition after explicit microphone activation; manual turn-taking.
3. Reusable speech input/output adapters and deterministic quality tests.
4. Evaluate a genuinely conversational model and streaming voice stack **only after** a reviewed zero-cost or authorized cost plan.
5. Add real phone integrations only after business consent, provider readiness, privacy controls, and explicit spending approval.

**Cost boundary:** $0 new spend. No Railway service, live provider calls, purchased domains, or deployment from this document.

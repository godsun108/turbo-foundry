# Foundry Autopilot — First revenue decision plan

Status: **pre-sales / offline demo only**. No active customer, validated revenue, delivery integration, customer SMS or billing is claimed.

## Product to sell (only once legally/operationally ready)

Missed-call lead recovery for small local service businesses: a measurable, consent-aware follow-up workflow with suppression, business hours, and a clear human handoff. The product's value proposition is *faster response and measurable outcomes*, not guaranteed appointments.

## Fastest responsible route to first revenue

1. **This week: discovery, no money collected.** Invite 10 relevant local service businesses to a 15-minute conversation about missed-call volume, existing phone system, opt-in evidence, lead values, compliance requirements, after-hours handling and response time. Document the source of every estimate; do not import caller numbers or private records into public tools.
2. **Qualify at least 3.** A viable pilot must have a named decision maker, explicit interest in a follow-up pilot, a phone/CRM integration path, an acceptable consent and opt-out approach, and enough missed-call volume to make a paid solution plausible.
3. **Offline demo.** Show `python -m src.autopilot.demo` and a clear explanation that SMS and recovered bookings are simulated. Collect specific objections and willingness to pay; do not claim operational readiness.
4. **Scenario math.** Use `src/autopilot/pilot_economics.py` for bounded what-if estimates. Inputs are assumptions, not measured revenue. Test conservative/base/optimistic cases and calculate contribution after estimated delivery costs. The customer net excludes all costs not included in the stated gross margin; the provider contribution excludes staff/support, taxes, marketing and setup.
5. **Pilot readiness gate.** Before signing a live-service agreement or accepting payment for an operational service, obtain documented customer authorization, verify phone-provider ownership/account binding and operational security, review messaging consent and applicable rules with qualified counsel, prove opt-outs/retries/delivery reconciliation, establish support/incident response, and approve an accurate written scope, payment and cancellation terms.
6. **Run one authorized pilot**, measure actual eligible missed calls, successful delivery, response, confirmed bookings and *collected* attributable revenue. Extend only if measured performance and unit economics justify it.

## Discovery script (research, not an offer of a live service)

“I'm researching a missed-call follow-up tool for service businesses. How often do new customers reach voicemail or call after hours? What happens to those leads today? What would faster, permission-based follow-up be worth if we could demonstrate it safely? Could I show you an offline demo and get your feedback?”

Ask about the current consent workflow, SMS opt-outs, phone provider, average realized gross margin on booked work, busy hours, and willingness to participate in a later explicitly approved pilot. Do not make unsolicited automated marketing calls/messages through the prototype.

## Go/no-go scorecard

| Gate | Current evidence | Outcome |
| --- | --- | --- |
| Offline product/demo | Synthetic demo and CI | Demonstration only |
| Prospect interest | No recorded qualified discovery | Unproven |
| Compliant real-world consent | No approved provider/customer flow | Blocked |
| Operating identity separation | Privileged two-UID test authored, not yet executed | Blocked |
| SMS sending / delivery proof | Synthetic only | Blocked |
| Payment acceptance / refund/support terms | Not set up for this offer | Blocked |
| Actual attributable recovered sales | None recorded | Not demonstrated |

**Priority:** validate demand before building more speculative infrastructure. A discovery call and a realistic pilot cost estimate can guide engineering better than another dozen security-only sprints. Never mark simulated bookings as customer outcomes.

## Pricing

No public price has been set. Example scenarios such as $299 per month are **assumptions for arithmetic**, not approved pricing or a request to pay. Price only after comparing provider fees, labor/support, compliance costs, measured customer value and actual willingness to pay.

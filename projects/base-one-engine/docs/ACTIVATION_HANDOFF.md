# Scout Live — Human Activation Handoff

The code side is ready. The remaining step requires an authorized human/account holder because MLS data licenses bind to a broker, agent, participant, subscriber, or approved vendor.

## MCRTC / Trestle
MCRTC says vendors request connections through Cotality/CoreLogic Trestle and that contracts are required for the agent/broker receiving vendor services:
https://martincountyrealtors.org/data-feeds/

## BeachesMLS
BeachesMLS documents direct Agent/Broker licensed feeds through FBS Datamart WebAPI and Trestle. Approval from BeachesMLS (and, where applicable, the broker/subscriber) is required:
https://beachesmls.zendesk.com/hc/en-us/articles/42465686846356-What-are-my-IDX-options-as-a-BeachesMLS-Agent

## What Base One needs after approval
- Web API endpoint
- authorized API token/key
- provider metadata URL/response if supplied
- permitted data-use category

Put credentials in GitHub Secrets, never source files.

Once credentials exist, run **Base One Scout Live** manually once, validate mappings, then leave the daily schedule enabled.

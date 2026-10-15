"""Opt-in model-backed Foundry reply generator for a trusted server-side LLM API.

Compatible with chat-completions style APIs; no provider is configured by
default. No external actions, payments, or booking confirmations. Model output
is always untrusted and validated by the existing Genesis contract.
"""
import json
import urllib.parse
import urllib.request
from .genesis_reply_contract import validate_genesis_reply


class ModelReplyGenerator:
    def __init__(self, *, endpoint, model, api_key, opener=None, timeout=5):
        url = urllib.parse.urlsplit(endpoint)
        if (url.scheme != "https" or not url.hostname or url.username or url.password
                or url.query or url.fragment or not url.path.endswith("/chat/completions")
                or not isinstance(model, str) or not 1 <= len(model) <= 100
                or not isinstance(api_key, str) or len(api_key) < 16
                or not 0.1 <= timeout <= 10):
            raise ValueError("invalid model configuration")
        self.endpoint, self.model, self.key = endpoint, model, api_key
        self.opener, self.timeout = opener or urllib.request.urlopen, timeout

    def __call__(self, turn):
        if not isinstance(turn, dict) or turn.get("schema") != "foundry.genesis.turn.v0":
            raise ValueError("invalid turn")
        utterance = turn.get("utterance")
        if not isinstance(utterance, str) or not 1 <= len(utterance) <= 1000:
            raise ValueError("invalid utterance")
        facts = turn.get("verified_business_facts", {})
        if (not isinstance(facts, dict) or set(facts) - {"business_name", "service_area", "services"}
                or any(not isinstance(v, str) or len(v) > 160 for v in facts.values())):
            raise ValueError("invalid business facts")
        history = turn.get("context", [])
        if (not isinstance(history, list) or len(history) > 20
                or any(not isinstance(h, dict) or h.get("role") not in ("user", "assistant")
                       or not isinstance(h.get("content"), str) or len(h["content"]) > 1200 for h in history)):
            raise ValueError("invalid history")
        instructions = (
            "You are a clearly identified AI customer-service assistant in a controlled demo. "
            "Only use the provided verified business facts; never invent hours, pricing, "
            "service coverage, appointment availability, or completed actions. "
            "Do not claim to send messages, book appointments, contact staff, or provide emergency help. "
            "Respond with one JSON object with exactly these keys: schema, reply, intent, "
            "disposition, proposed_actions, evidence, verified_booking, real_message_sent. "
            "schema must be foundry.genesis.reply.v0; proposed_actions and evidence must be []; "
            "verified_booking and real_message_sent must be false. "
            "intent must be one of intake, quote_request, appointment_request, support. "
            "disposition must be collect_details or informational. "
            "Keep reply under 600 characters. Verified facts: " + json.dumps(facts, ensure_ascii=True)
        )
        messages = [{"role": "system", "content": instructions}]
        messages += [{"role": h["role"], "content": h["content"]} for h in history]
        messages.append({"role": "user", "content": utterance})
        body = json.dumps({"model": self.model, "messages": messages,
                           "temperature": 0.2, "max_tokens": 300,
                           "response_format": {"type": "json_object"}}).encode()
        if len(body) > 32768:
            raise ValueError("request too large")
        request = urllib.request.Request(self.endpoint, data=body, method="POST",
            headers={"Authorization": "Bearer " + self.key,
                     "Content-Type": "application/json", "Accept": "application/json"})
        with self.opener(request, timeout=self.timeout) as response:
            if response.status != 200:
                raise ValueError("model unavailable")
            raw = response.read(16385)
        if len(raw) > 16384:
            raise ValueError("model response too large")
        envelope = json.loads(raw)
        candidate = json.loads(envelope["choices"][0]["message"]["content"])
        validate_genesis_reply(candidate)
        return candidate

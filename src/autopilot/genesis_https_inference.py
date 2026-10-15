"""Server-side, opt-in HTTPS transport for a *compatible* Genesis inference API.

Does not enable hosting, billing, customer traffic, or claim that First Contact
implements this schema. Never put access tokens in a browser. Fail closed.
"""
import json
import urllib.request
import urllib.parse
from .genesis_reply_contract import validate_genesis_reply


class GenesisHTTPSInference:
    def __init__(self, *, endpoint, bearer_token, timeout=3.0, opener=None):
        parsed = urllib.parse.urlsplit(endpoint)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username
                or parsed.password or parsed.fragment or parsed.query
                or not isinstance(bearer_token, str) or len(bearer_token) < 24
                or not 0.1 <= timeout <= 10.0):
            raise ValueError("invalid server-side Genesis transport configuration")
        self._endpoint = endpoint
        self._token = bearer_token
        self._timeout = timeout
        self._opener = opener or urllib.request.urlopen

    def __call__(self, payload):
        if not isinstance(payload, dict) or payload.get("schema") != "foundry.genesis.turn.v0":
            raise ValueError("unsupported request")
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        if len(data) > 16_384:
            raise ValueError("oversized inference request")
        request = urllib.request.Request(
            self._endpoint, data=data, method="POST",
            headers={"Authorization": "Bearer " + self._token,
                     "Content-Type": "application/json", "Accept": "application/json"})
        with self._opener(request, timeout=self._timeout) as response:
            if response.status != 200:
                raise ValueError("inference unavailable")
            raw = response.read(8193)
        if len(raw) > 8192:
            raise ValueError("oversized inference response")
        candidate = json.loads(raw)
        validate_genesis_reply(candidate)
        return candidate

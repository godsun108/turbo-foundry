"""Trusted account authentication before atomic call-event persistence."""
from datetime import datetime
from typing import Mapping
from .account_auth import TrustedAccountVerifier
from .atomic_ingest import AtomicCallIngest
from .call_journal import JournalResult

class VerifiedAtomicIngest:
    def __init__(self, db_path: str, tokens_by_account: Mapping[str,str]):
        self.verifier=TrustedAccountVerifier(tokens_by_account)
        self.ingest=AtomicCallIngest(db_path)

    def record(self, *, tenant_id: str | None, provisioned_number: str | None,
               url: str, params: Mapping[str,str], signature: str,
               event_key: str, received_at: datetime,
               validator_factory=None) -> JournalResult:
        verified=self.verifier.verify(url=url,params=params,signature=signature,
                                      validator_factory=validator_factory)
        if not verified.verified:
            return JournalResult(False,verified.reason)
        token=self.verifier._tokens[verified.account_sid]
        validator=validator_factory(token) if validator_factory else None
        return self.ingest.record(
            tenant_id=tenant_id,provisioned_number=provisioned_number,
            url=url,params=params,signature=signature,auth_token=token,
            event_key=event_key,received_at=received_at,
            provider_account_sid=verified.account_sid,validator=validator)

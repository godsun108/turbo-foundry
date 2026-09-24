"""Property intake and provenance for Base One Engine."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional
import hashlib, json

@dataclass(frozen=True)
class Source:
    kind: str
    reference: str
    retrieved_at: str
    notes: str = ""

@dataclass(frozen=True)
class PropertyRecord:
    address: str
    asking_price: float
    property_type: str
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[float] = None
    annual_property_tax: Optional[float] = None
    annual_insurance_estimate: Optional[float] = None
    monthly_rent_estimate: Optional[float] = None
    rehab_estimate: Optional[float] = None

    def validate(self):
        if not self.address.strip(): raise ValueError("address is required")
        if self.asking_price <= 0: raise ValueError("asking_price must be positive")
        for k,v in asdict(self).items():
            if isinstance(v,(int,float)) and k!="asking_price" and v is not None and v < 0:
                raise ValueError(f"{k} cannot be negative")

def utc_now()->str:
    return datetime.now(timezone.utc).isoformat()

def make_deal_record(property_record:PropertyRecord,sources:list[Source],
                     assumptions:dict|None=None)->dict:
    property_record.validate()
    if not sources: raise ValueError("at least one source is required")
    payload={
        "schema_version":"base-one-intake-v0.1",
        "property":asdict(property_record),
        "sources":[asdict(s) for s in sources],
        "assumptions":assumptions or {},
    }
    canonical=json.dumps(payload,sort_keys=True,separators=(",",":"))
    payload["record_sha256"]=hashlib.sha256(canonical.encode()).hexdigest()
    return payload

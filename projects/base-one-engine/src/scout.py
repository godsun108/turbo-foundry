"""Base One Scout: source-agnostic candidate discovery and change detection."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable
import hashlib, json

@dataclass(frozen=True)
class ScoutCriteria:
    locations: tuple[str,...]=()
    max_asking_price: float|None=None
    property_types: tuple[str,...]=()
    min_bedrooms: float|None=None
    min_square_feet: float|None=None

@dataclass(frozen=True)
class Candidate:
    source_kind: str
    source_reference: str
    retrieved_at: str
    address: str
    asking_price: float
    property_type: str
    bedrooms: float|None=None
    bathrooms: float|None=None
    square_feet: float|None=None

    def fingerprint(self)->str:
        body=json.dumps(asdict(self),sort_keys=True,separators=(",",":"))
        return hashlib.sha256(body.encode()).hexdigest()

def matches(c:Candidate,q:ScoutCriteria)->bool:
    if c.asking_price<=0: return False
    if q.locations and not any(x.lower() in c.address.lower() for x in q.locations): return False
    if q.max_asking_price is not None and c.asking_price>q.max_asking_price: return False
    if q.property_types and c.property_type not in q.property_types: return False
    if q.min_bedrooms is not None and (c.bedrooms is None or c.bedrooms<q.min_bedrooms): return False
    if q.min_square_feet is not None and (c.square_feet is None or c.square_feet<q.min_square_feet): return False
    return True

def discover(candidates:Iterable[Candidate],criteria:ScoutCriteria)->list[Candidate]:
    return sorted((c for c in candidates if matches(c,criteria)),
                  key=lambda c:(c.asking_price,c.address,c.source_reference))

def detect_changes(previous:list[Candidate],current:list[Candidate])->dict:
    key=lambda c:(c.source_kind,c.source_reference)
    old={key(c):c for c in previous}; new={key(c):c for c in current}
    added=[new[k] for k in new.keys()-old.keys()]
    removed=[old[k] for k in old.keys()-new.keys()]
    changed=[]
    for k in new.keys()&old.keys():
        if old[k].fingerprint()!=new[k].fingerprint():
            changed.append({"before":old[k],"after":new[k]})
    return {"added":added,"changed":changed,"removed":removed}

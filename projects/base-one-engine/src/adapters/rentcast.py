"""RentCast active-sale adapter for Base One Scout.

Self-serve API-key integration; no MLS broker relationship is assumed.
Docs: https://developers.rentcast.io/reference/sale-listings
"""
from __future__ import annotations
import json, os, urllib.parse, urllib.request
from datetime import datetime, timezone
from scout import Candidate

BASE="https://api.rentcast.io/v1/listings/sale"

def _num(v):
    try: return float(v) if v not in (None,"") else None
    except (TypeError,ValueError): return None

def normalize(row:dict,retrieved_at:str|None=None)->Candidate:
    price=_num(row.get("price"))
    if price is None or price<=0: raise ValueError("listing has no positive price")
    status=str(row.get("status") or "")
    if status and status.lower()!="active": raise ValueError("listing is not active")
    address=row.get("formattedAddress") or ", ".join(str(x) for x in
        [row.get("addressLine1"),row.get("city"),row.get("state"),row.get("zipCode")] if x)
    ref=row.get("id") or address
    return Candidate(
      source_kind="rentcast_active_listing",
      source_reference=f"rentcast:{ref}",
      retrieved_at=retrieved_at or datetime.now(timezone.utc).isoformat(),
      address=address,asking_price=price,
      property_type=str(row.get("propertyType") or "unknown"),
      bedrooms=_num(row.get("bedrooms")),bathrooms=_num(row.get("bathrooms")),
      square_feet=_num(row.get("squareFootage")))

def fetch_city(api_key:str,city:str,state="FL",limit=500,extra:dict|None=None)->list[dict]:
    q={"city":city,"state":state,"status":"Active","limit":str(limit)}
    q.update(extra or {})
    req=urllib.request.Request(BASE+"?"+urllib.parse.urlencode(q),
      headers={"X-Api-Key":api_key,"Accept":"application/json","User-Agent":"Base-One-Scout/0.5"})
    with urllib.request.urlopen(req,timeout=60) as r: body=json.load(r)
    if not isinstance(body,list): raise RuntimeError(f"unexpected RentCast response: {body}")
    return body

def fetch_target_cities(cities:list[str],state="FL",limit=500)->list[Candidate]:
    key=os.environ.get("RENTCAST_API_KEY")
    if not key: raise RuntimeError("RENTCAST_API_KEY is required")
    ts=datetime.now(timezone.utc).isoformat(); out=[]; seen=set()
    for city in cities:
        for row in fetch_city(key,city,state,limit):
            try: c=normalize(row,ts)
            except ValueError: continue
            if c.source_reference not in seen:
                seen.add(c.source_reference); out.append(c)
    return out

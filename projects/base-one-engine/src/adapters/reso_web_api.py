"""RESO Web API active-listing adapter for Base One Scout.

Requires a licensed MLS/provider endpoint and bearer token. No credentials are
hard-coded. The adapter consumes standard RESO/OData-style Property resources.
"""
from __future__ import annotations
import json, os, urllib.parse, urllib.request
from datetime import datetime, timezone
from scout import Candidate

SELECT=("ListingKey,ListPrice,StandardStatus,PropertyType,BedroomsTotal,"
        "BathroomsTotalInteger,LivingArea,UnparsedAddress,City,StateOrProvince,"
        "PostalCode,ModificationTimestamp")

def _num(v):
    try: return float(v) if v not in (None,"") else None
    except (TypeError,ValueError): return None

def normalize(row:dict,retrieved_at:str|None=None)->Candidate:
    price=_num(row.get("ListPrice"))
    if price is None or price<=0: raise ValueError("listing has no positive ListPrice")
    address=row.get("UnparsedAddress") or ""
    locality=", ".join(str(x) for x in [row.get("City"),row.get("StateOrProvince"),row.get("PostalCode")] if x)
    full=", ".join(x for x in [address,locality] if x)
    return Candidate(
        source_kind="reso_active_listing",
        source_reference=f"listing:{row.get('ListingKey')}",
        retrieved_at=retrieved_at or datetime.now(timezone.utc).isoformat(),
        address=full,asking_price=price,
        property_type=str(row.get("PropertyType") or "unknown"),
        bedrooms=_num(row.get("BedroomsTotal")),
        bathrooms=_num(row.get("BathroomsTotalInteger")),
        square_feet=_num(row.get("LivingArea")),
    )

def fetch(endpoint:str,token:str,filter_expr:str,top:int=200)->list[dict]:
    base=endpoint.rstrip("/")+"/Property"
    params={"$filter":filter_expr,"$select":SELECT,"$top":str(top),
            "$orderby":"ModificationTimestamp desc"}
    url=base+"?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}",
                                           "Accept":"application/json",
                                           "User-Agent":"Base-One-Scout/0.4"})
    with urllib.request.urlopen(req,timeout=60) as r: body=json.load(r)
    if "error" in body: raise RuntimeError(body["error"])
    return body.get("value",[])

def fetch_from_env(filter_expr:str,top:int=200)->list[Candidate]:
    endpoint=os.environ.get("RESO_ENDPOINT")
    token=os.environ.get("RESO_TOKEN")
    if not endpoint or not token:
        raise RuntimeError("RESO_ENDPOINT and RESO_TOKEN are required")
    ts=datetime.now(timezone.utc).isoformat()
    out=[]
    for row in fetch(endpoint,token,filter_expr,top):
        try: out.append(normalize(row,ts))
        except ValueError: pass
    return out

"""Public-record adapter for St. Lucie County Property Appraiser ArcGIS parcels.

This is enrichment/discovery from public assessment records, NOT an active-for-sale
listing feed. SalePrice is historical transaction data, never asking price.
"""
from __future__ import annotations
import json, urllib.parse, urllib.request
from datetime import datetime, timezone
from scout import Candidate

ENDPOINT="https://map.paslc.gov/arcgis/rest/services/GISPublic/TaxMap/MapServer/9/query"
FIELDS="ParcelID,PropertyID,LandUseCodeDescription,TotalArea,YearBuilt,Beds,Baths,SiteAddress,SiteCity,SiteZIP,SalePrice,SaleDate,TotalAppraisedValue,TotalAssessedValue,TotalTaxableValue,Zoning"

def fetch(where="SiteCity IS NOT NULL",limit=500)->list[dict]:
    params={"where":where,"outFields":FIELDS,"returnGeometry":"false","f":"json",
            "resultRecordCount":str(limit),"orderByFields":"PropertyID ASC"}
    url=ENDPOINT+"?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":"Base-One-Scout/0.3 public-record-research"})
    with urllib.request.urlopen(req,timeout=60) as r:
        body=json.load(r)
    if "error" in body: raise RuntimeError(body["error"])
    return [x["attributes"] for x in body.get("features",[])]

def normalize(row:dict,retrieved_at:str|None=None)->Candidate:
    retrieved_at=retrieved_at or datetime.now(timezone.utc).isoformat()
    address=", ".join(x for x in [row.get("SiteAddress"),row.get("SiteCity"),"FL",row.get("SiteZIP")] if x)
    # Candidate requires a positive price, but assessment records do not supply asking price.
    # Use appraised value ONLY as a public-record reference value and identify the source kind.
    ref=float(row.get("TotalAppraisedValue") or 0)
    if ref<=0: raise ValueError("record has no positive appraised reference value")
    beds=row.get("Beds")
    try: beds=float(beds) if beds not in (None,"") else None
    except (TypeError,ValueError): beds=None
    return Candidate(
      source_kind="st_lucie_property_appraiser_reference",
      source_reference=f"parcel:{row.get('ParcelID') or row.get('PropertyID')}",
      retrieved_at=retrieved_at,address=address,asking_price=ref,
      property_type=str(row.get("LandUseCodeDescription") or "unknown"),
      bedrooms=beds,bathrooms=row.get("Baths"),square_feet=None)

def fetch_normalized(where="SiteCity IS NOT NULL",limit=500)->list[Candidate]:
    ts=datetime.now(timezone.utc).isoformat()
    out=[]
    for row in fetch(where,limit):
        try: out.append(normalize(row,ts))
        except ValueError: pass
    return out

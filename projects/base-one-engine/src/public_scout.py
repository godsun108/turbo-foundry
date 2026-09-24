"""Public-data Scout pipeline.

Queries St. Lucie public parcel records, applies explicit parcel criteria, and
writes reproducible candidate artifacts. Public records are NOT current listings.
"""
from __future__ import annotations
import argparse,csv,json
from dataclasses import asdict
from pathlib import Path
from adapters.st_lucie_parcels import fetch

TARGET_CITIES={"PORT ST LUCIE","PORT SAINT LUCIE","JENSEN BEACH","STUART"}

def _num(v):
    try:return float(v) if v not in (None,"") else None
    except (TypeError,ValueError):return None

def select(rows:list[dict],max_appraised:float|None=None,min_beds:float|None=None)->list[dict]:
    out=[]
    for r in rows:
        city=str(r.get("SiteCity") or "").upper().strip()
        if city not in TARGET_CITIES: continue
        value=_num(r.get("TotalAppraisedValue"))
        beds=_num(r.get("Beds"))
        if max_appraised is not None and (value is None or value>max_appraised): continue
        if min_beds is not None and (beds is None or beds<min_beds): continue
        out.append({
          "parcel_id":r.get("ParcelID"),"property_id":r.get("PropertyID"),
          "address":r.get("SiteAddress"),"city":r.get("SiteCity"),"zip":r.get("SiteZIP"),
          "land_use":r.get("LandUseCodeDescription"),"year_built":r.get("YearBuilt"),
          "beds":beds,"baths":_num(r.get("Baths")),"zoning":r.get("Zoning"),
          "appraised_value":value,"assessed_value":_num(r.get("TotalAssessedValue")),
          "taxable_value":_num(r.get("TotalTaxableValue")),
          "historical_sale_price":_num(r.get("SalePrice")),"historical_sale_date":r.get("SaleDate")
        })
    return sorted(out,key=lambda x:((x["appraised_value"] is None),x["appraised_value"] or 0,x["city"] or "",x["address"] or ""))

def write(rows:list[dict],outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"public-scout.json").write_text(json.dumps(rows,indent=2,sort_keys=True)+"\n")
    if rows:
        with (outdir/"public-scout.csv").open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (outdir/"NOTICE.txt").write_text(
      "PUBLIC RECORD CANDIDATES ONLY. These are not active-for-sale listings. "
      "Appraised/assessed/historical sale values are not asking prices.\n")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--limit",type=int,default=2000)
    p.add_argument("--max-appraised",type=float)
    p.add_argument("--min-beds",type=float)
    p.add_argument("--outdir",type=Path,default=Path("outputs/public"))
    a=p.parse_args()
    rows=select(fetch("SiteCity IS NOT NULL",a.limit),a.max_appraised,a.min_beds)
    write(rows,a.outdir);print("public-record candidates:",len(rows))
if __name__=="__main__":main()

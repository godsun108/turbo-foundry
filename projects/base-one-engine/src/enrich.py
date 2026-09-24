"""Join active listings to public-record candidates conservatively by normalized address."""
from __future__ import annotations
import re
from scout import Candidate

def norm_address(s:str)->str:
    s=s.upper().replace("PORT SAINT LUCIE","PORT ST LUCIE")
    s=re.sub(r"[^A-Z0-9 ]+"," ",s)
    return " ".join(s.split())

def join_public_records(listings:list[Candidate],parcels:list[Candidate])->list[dict]:
    index={}
    for p in parcels: index.setdefault(norm_address(p.address),[]).append(p)
    out=[]
    for x in listings:
        matches=index.get(norm_address(x.address),[])
        out.append({"listing":x,"public_record":matches[0] if len(matches)==1 else None,
                    "match_status":"exact_unique" if len(matches)==1 else
                    ("ambiguous" if len(matches)>1 else "not_found")})
    return out

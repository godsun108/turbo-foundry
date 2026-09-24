"""Produce an explainable Scout shortlist from active candidates."""
from __future__ import annotations
from scout import Candidate
from scout_rank import score

def shortlist(candidates:list[Candidate],max_price:float|None=None,limit:int=25)->list[dict]:
    rows=[{"candidate":c,"triage":score(c,max_price)} for c in candidates]
    rows.sort(key=lambda x:(-x["triage"]["priority_score"],x["candidate"].asking_price,x["candidate"].address))
    return rows[:max(1,limit)]

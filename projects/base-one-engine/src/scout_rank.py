"""Transparent prioritization for Scout candidates.

This is a triage score, not a purchase recommendation. Missing facts never
receive favorable assumptions.
"""
from __future__ import annotations
from dataclasses import dataclass
from scout import Candidate

@dataclass(frozen=True)
class PriorityWeights:
    price: float=0.35
    bedrooms: float=0.15
    size: float=0.15
    completeness: float=0.35

def _bounded(v,lo,hi):
    if hi<=lo: return 0.0
    return max(0.0,min(1.0,(v-lo)/(hi-lo)))

def score(c:Candidate, max_price:float|None=None, weights:PriorityWeights=PriorityWeights())->dict:
    completeness=sum(x is not None for x in (c.bedrooms,c.bathrooms,c.square_feet))/3
    price_component=0.5
    if max_price and max_price>0:
        price_component=max(0.0,min(1.0,(max_price-c.asking_price)/max_price))
    bed_component=_bounded(c.bedrooms or 0,1,4) if c.bedrooms is not None else 0
    size_component=_bounded(c.square_feet or 0,700,2200) if c.square_feet is not None else 0
    total=(price_component*weights.price+bed_component*weights.bedrooms+
           size_component*weights.size+completeness*weights.completeness)
    return {"priority_score":round(total,6),"components":{
      "price":round(price_component,6),"bedrooms":round(bed_component,6),
      "size":round(size_component,6),"completeness":round(completeness,6)},
      "warning":"Triage only; not a buy/sell recommendation."}

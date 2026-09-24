"""Scheduled Scout runner with persistent snapshot/change artifacts."""
from __future__ import annotations
import argparse, json
from dataclasses import asdict
from pathlib import Path
from scout import Candidate, ScoutCriteria, discover, detect_changes
from adapters.manual_json import load_candidates

def load_criteria(path:Path)->ScoutCriteria:
    d=json.loads(path.read_text())
    for k in ("locations","property_types"):
        if k in d and d[k] is not None: d[k]=tuple(d[k])
    return ScoutCriteria(**d)

def load_snapshot(path:Path)->list[Candidate]:
    if not path.exists(): return []
    return [Candidate(**x) for x in json.loads(path.read_text())]

def run(source:Path,config:Path,state:Path,outdir:Path)->dict:
    criteria=load_criteria(config)
    current=discover(load_candidates(source),criteria)
    previous=load_snapshot(state)
    changes=detect_changes(previous,current)
    outdir.mkdir(parents=True,exist_ok=True); state.parent.mkdir(parents=True,exist_ok=True)
    serial=[asdict(x) for x in current]
    state.write_text(json.dumps(serial,indent=2,sort_keys=True)+"\n")
    def enc(x):
        if isinstance(x,Candidate): return asdict(x)
        if isinstance(x,dict): return {k:enc(v) for k,v in x.items()}
        if isinstance(x,list): return [enc(v) for v in x]
        return x
    report={"candidate_count":len(current),"changes":enc(changes)}
    (outdir/"scout-latest.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--config",type=Path,required=True)
    p.add_argument("--state",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    r=run(a.source,a.config,a.state,a.outdir)
    print(json.dumps({"candidate_count":r["candidate_count"],
      "added":len(r["changes"]["added"]),"changed":len(r["changes"]["changed"]),
      "removed":len(r["changes"]["removed"])}))

if __name__=="__main__": main()

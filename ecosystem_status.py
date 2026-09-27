#!/usr/bin/env python3
import json
from pathlib import Path

REGISTRY = Path("ECOSYSTEM.json")

def load():
    data=json.loads(REGISTRY.read_text())
    assert data.get("schema")=="turbo.ecosystem.v1"
    systems=data.get("systems")
    assert isinstance(systems,list) and systems
    ids=[s.get("id") for s in systems]
    assert all(ids) and len(ids)==len(set(ids))
    return data

def render(data):
    systems=data["systems"]
    by_id={s["id"]:s for s in systems}
    lines=["# TURBO ECOSYSTEM STATUS","","> Generated deterministically from `ECOSYSTEM.json`. This is an architecture/contract status surface, not a network uptime claim.","",f"Canonical registry: **{len(systems)} systems**","","| System | Role | Repository | Contracts | Status |","|---|---|---|---:|---|"]
    for s in systems:
        repo=s.get("repo") or "not recovered"
        status=s.get("status","registered")
        lines.append(f"| `{s['id']}` | {s.get('role','')} | {repo} | {len(s.get('contracts',[]))} | {status} |")
    lines+=["","## Dependency edges",""]
    edges=0
    for s in systems:
        for dep in s.get("consumes",[]):
            target=dep.get("system")
            assert target in by_id, f"unknown dependency target: {target}"
            via=dep.get("via","declared contract")
            exp=dep.get("experience")
            lines.append(f"- `{s['id']}` → `{target}` via {via}"+(f" ({exp})" if exp else ""))
            edges+=1
    if not edges: lines.append("- No dependency edges declared.")
    lines+=["","## Recovery / legacy boundaries",""]
    bounded=[s for s in systems if s.get("boundary") or s.get("status")]
    for s in bounded:
        lines.append(f"- **{s['id']}** — {s.get('status','registered')}: {s.get('boundary','No additional boundary declared.')}")
    lines+=["","## Registry checks","","- schema recognized","- system IDs unique","- declared dependency targets exist","- status generated without external network assumptions",""]
    return "\n".join(lines)

if __name__=="__main__":
    data=load()
    Path("ECOSYSTEM_STATUS.md").write_text(render(data))
    print("ecosystem registry verified")

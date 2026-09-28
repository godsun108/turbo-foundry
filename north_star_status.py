#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ECOSYSTEM = Path("ECOSYSTEM.json")
NORTH_STARS = Path("NORTH_STARS.json")
OUTPUT = Path("NORTH_STAR_STATUS.md")

def load():
    ecosystem = json.loads(ECOSYSTEM.read_text())
    north = json.loads(NORTH_STARS.read_text())
    assert ecosystem.get("schema") == "turbo.ecosystem.v1"
    assert north.get("schema") == "turbo.north-stars.v1"
    owners = {s["id"] for s in ecosystem["systems"]}
    allowed = set(north["states"])
    entries = north["entries"]
    ids = [e["id"] for e in entries]
    assert entries and len(ids) == len(set(ids)), "North Star IDs must be unique"
    for e in entries:
        assert e["owner"] in owners, f"unknown canonical owner: {e['owner']}"
        assert e["state"] in allowed, f"unknown maturity state: {e['state']}"
        assert e["north_star"].strip() and e["next_proof"].strip()
        proof = e.get("proof", {})
        assert proof.get("status") in {"UNVERIFIED", "VERIFIED", "FAILED", "INCONCLUSIVE"}
        assert isinstance(proof.get("evidence"), list)
        if proof["status"] == "VERIFIED":
            assert proof["evidence"], f"verified proof requires evidence: {e['id']}"
    return north

def render(data):
    entries = data["entries"]
    counts = Counter(e["state"] for e in entries)
    lines = [
        "# NORTH STAR MISSION COMMAND",
        "",
        "> Generated deterministically from `NORTH_STARS.json`. Maturity is a declared evidence state; proof status is separate and never inferred from repository activity.",
        "",
        f"Tracked North Stars: **{len(entries)}**",
        "",
        "## Maturity distribution",
        "",
    ]
    for state in data["states"]:
        lines.append(f"- **{state}**: {counts.get(state, 0)}")
    lines += [
        "",
        "## Proof queue",
        "",
        "| System | Owner | Maturity | Proof | Next decisive proof event |",
        "|---|---|---|---|---|",
    ]
    for e in entries:
        lines.append(
            f"| **{e['name']}** | `{e['owner']}` | {e['state']} | {e['proof']['status']} | {e['next_proof']} |"
        )
    lines += ["", "## North Stars", ""]
    for e in entries:
        lines += [
            f"### {e['name']}",
            f"- **North Star:** {e['north_star']}",
            f"- **Canonical owner:** `{e['owner']}`",
            f"- **Maturity:** {e['state']}",
            f"- **Proof status:** {e['proof']['status']}",
            f"- **Next proof:** {e['next_proof']}",
        ]
        evidence = e["proof"]["evidence"]
        if evidence:
            lines.append("- **Evidence:** " + "; ".join(str(x) for x in evidence))
        lines.append("")
    lines += [
        "## Truth rules",
        "",
        "- Repository size, commit count and recent activity do not promote maturity.",
        "- Proof is never inferred from a filename or implementation claim.",
        "- `VERIFIED` requires explicit preserved evidence.",
        "- Failed and inconclusive proof events remain evidence.",
        "- Simulation, paper, testnet, live, paid and settled states must remain distinct.",
        "- Human authorization boundaries remain independent from research output.",
        "",
    ]
    return "\n".join(lines)

if __name__ == "__main__":
    data = load()
    OUTPUT.write_text(render(data).rstrip() + "\n")
    print(f"north star registry verified: {len(data['entries'])} entries")

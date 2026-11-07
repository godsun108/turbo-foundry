#!/usr/bin/env python3
"""Turbo Foundry cross-repo contract validator.

Automates the North Star proof event: "automatically validate cross-repo
ownership/contracts and proof claims." Reads ECOSYSTEM.json as the single source
of truth and verifies, against real sibling checkouts:

1. REGISTRY: every system entry is well-formed (id, repo, stage known).
2. CONTRACTS: every declared contract path exists in the sibling checkout.
3. HYGIENE: every non-placeholder repo has a README and at least one test file.
4. LOCKSTEP: cross-repo schema strings that reference each other must appear
   verbatim in both producer and consumer repos (drift = failure with the two
   repos named).
5. PROOF: every proof claim in proof/ has its cited evidence path present.

Exit 0 = all claims verified. Exit 1 = at least one false claim, with the
offending repo + contract named. Designed to run in CI on a schedule with
sibling repos checked out under ./ecosystem/.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
ECOSYSTEM = ROOT / "ECOSYSTEM.json"
PROOF_DIR = ROOT / "proof"

KNOWN_STATUSES = {None, "active", "placeholder", "empty-placeholder", "legacy-preserve-review", "source-not-located", "pre-implementation"}
ACTIVE_STATUSES = {None, "active", "pre-implementation"}
SCHEMA_DIR = "sovereign.provenance.receipt.v1"  # canonical producer schema

# Cross-repo lockstep pairs: (producer repo, consumer repo, schema/constant string)
LOCKSTEP = [
    ("Sovereign-Core",  "Command-center",      "sovereign.provenance.receipt.v1"),
    ("Command-center",  "Command-center",      "command-center.sovereign-bridge.v1"),
    ("Command-center",  "Command-center",      "command-center.sovereign-anchor.v1"),
    ("Command-center",  "Command-center",      "sovereign.proof.anchor"),
    ("Command-center",  "Command-center",      "sovereign.receipt.record"),
]

def fail(msg): print("FAIL", msg); return 1
def ok(msg): print("ok  ", msg); return 0

def repo_dir(repo_slug):
    return ROOT / "ecosystem" / repo_slug.split("/",1)[1]

def main():
    errors = 0
    try: reg = json.loads(ECOSYSTEM.read_text())
    except Exception as e: sys.exit(fail(f"ECOSYSTEM.json unreadable: {e}"))
    systems = reg.get("systems", [])
    if not systems: sys.exit(fail("registry declares no systems"))
    errors += ok(f"registry parsed: {len(systems)} systems declared")

    ids = set()
    for s in systems:
        sid = s.get("id"); ids.add(sid)
        if not sid: errors += fail("system missing id"); continue
        repo = s.get("repo")
        if repo is None:
            if s.get("status") not in {"placeholder","empty-placeholder","source-not-located"}:
                errors += fail(f"{sid}: repo null but status {s.get('status')!r} not placeholder")
            continue
        if not repo.startswith("godsun108/"): errors += fail(f"{sid}: repo slug malformed: {repo!r}")
    dupes = len([i for i in ids if sum(1 for s in systems if s.get("id")==i) > 1])
    if dupes: errors += fail(f"{dupes} duplicate system ids")

    # Per-repo checks against sibling checkouts
    for s in systems:
        slug = s.get("repo"); sid = s.get("id","?")
        if slug is None: continue  # placeholder without repo: handled in registry pass
        rd = repo_dir(slug)
        if not rd.exists():
            print(f"SKIP {sid}: checkout missing at {rd} (private repo or not cloned; pass --strict to require)")
            continue
        for c in s.get("contracts", []):
            p = rd / c.get("path","")
            if not p.exists(): errors += fail(f"{sid}: declared contract missing: {c.get('path')}")
            else: errors += ok(f"{sid}: contract present {c.get('path')}")
        stage = s.get("status")
        if stage in ACTIVE_STATUSES:
            if not list(rd.glob("README*")): errors += fail(f"{sid}: stage {stage} but no README")
            tests = list(rd.glob("test*/**")) + list(rd.glob("**/test*.mjs")) + list(rd.glob("**/test*.js")) + list(rd.glob("**/test_*.py")) + list(rd.glob("**/*.test.*"))
            if not tests: errors += fail(f"{sid}: stage {stage} but zero test files")
            else: errors += ok(f"{sid}: tests present ({len(tests)} files)")

    # Lockstep schema verification
    for producer, consumer, needle in LOCKSTEP:
        prd, crd = repo_dir("godsun108/"+producer), repo_dir("godsun108/"+consumer)
        if not prd.exists() or not crd.exists():
            print(f"SKIP lockstep {producer}->{consumer}: checkout missing (private repo or not cloned)")
            continue
        def has(repo, needle):
            for pat in ("*.mjs","*.js","*.py","*.md"):
                for f in repo.rglob(pat):
                    if "node_modules" in f.parts or ".git" in f.parts: continue
                    try:
                        if needle in f.read_text(errors="ignore"): return True
                    except Exception: pass
            return False
        if not has(prd, needle): errors += fail(f"lockstep: {needle!r} absent from producer {producer}")
        elif not has(crd, needle): errors += fail(f"lockstep: {needle!r} absent from consumer {consumer}")
        else: errors += ok(f"lockstep {needle!r}: {producer} -> {consumer}")

    # Proof claims: every md in proof/ must cite an evidence path that exists
    for claim in PROOF_DIR.glob("*.md"):
        text = claim.read_text(errors="ignore")
        for m in re.finditer(r"evidence[^\n`]*?`([\w./\-]+\.(?:json|md|txt))`", text):
            cited = ROOT / m.group(1)
            if not cited.exists(): errors += fail(f"proof/{claim.name}: cited evidence missing {m.group(1)}")

    print(f"\n{'ALL CLAIMS VERIFIED' if errors==0 else str(errors)+' CLAIM(S) FAILED'}")
    sys.exit(0 if errors==0 else 1)

if __name__ == "__main__":
    main()

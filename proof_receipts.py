#!/usr/bin/env python3
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "NORTH_STARS.json"
RECEIPTS = ROOT / "proof" / "receipts"
SHA256 = re.compile(r"^[a-f0-9]{64}$")
RID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,127}$")
ENVIRONMENTS = {"simulation","synthetic","historical","paper-forward","local","testnet","live","settled","recovery"}
RESULTS = {"PASS","FAIL","INCONCLUSIVE"}
KINDS = {"file","artifact","report","dataset","log","commit","url","other"}

def load_registry():
    data = json.loads(REGISTRY.read_text())
    return {e["id"]: e for e in data["entries"]}

def parse_time(value):
    assert isinstance(value, str) and value.endswith(("Z","+00:00")), "observed_at must be UTC ISO-8601"
    datetime.fromisoformat(value.replace("Z","+00:00"))

def validate_receipt(path, stars):
    d = json.loads(path.read_text())
    assert d.get("schema") == "turbo.proof-receipt.v1"
    allowed = {"schema","receipt_id","north_star_id","producer","observed_at","environment","claim","result","procedure","limitations","evidence"}
    assert set(d) <= allowed, f"unknown fields in {path}"
    required = {"schema","receipt_id","north_star_id","producer","observed_at","environment","claim","result","evidence"}
    assert required <= set(d), f"missing fields in {path}"
    rid = d["receipt_id"]
    assert RID.fullmatch(rid), f"invalid receipt_id: {rid}"
    assert path.stem == rid, f"filename must equal receipt_id: {path}"
    star_id = d["north_star_id"]
    assert star_id in stars, f"unknown north_star_id: {star_id}"
    assert path.parent.name == star_id, f"receipt directory must match north_star_id: {path}"
    producer = d["producer"]
    assert isinstance(producer, dict) and producer.get("system") == stars[star_id]["owner"], (
        f"producer must match canonical owner for {star_id}"
    )
    assert set(producer) <= {"system","repo","commit"}
    parse_time(d["observed_at"])
    assert d["environment"] in ENVIRONMENTS
    assert isinstance(d["claim"], str) and d["claim"].strip()
    assert d["result"] in RESULTS
    assert isinstance(d.get("limitations", []), list)
    evidence = d["evidence"]
    assert isinstance(evidence, list) and evidence, "receipt requires evidence"
    for item in evidence:
        assert set(item) <= {"kind","ref","sha256","description"}
        assert {"kind","ref","sha256"} <= set(item)
        assert item["kind"] in KINDS
        assert isinstance(item["ref"], str) and item["ref"].strip()
        assert SHA256.fullmatch(item["sha256"]), f"invalid sha256 in {path}"
    return d

def main():
    stars = load_registry()
    paths = sorted(RECEIPTS.glob("*/*.json")) if RECEIPTS.exists() else []
    seen = set()
    counts = {x: 0 for x in RESULTS}
    for path in paths:
        d = validate_receipt(path, stars)
        assert d["receipt_id"] not in seen, f"duplicate receipt_id: {d['receipt_id']}"
        seen.add(d["receipt_id"])
        counts[d["result"]] += 1
    print(f"proof receipts verified: {len(paths)} (PASS={counts['PASS']} FAIL={counts['FAIL']} INCONCLUSIVE={counts['INCONCLUSIVE']})")

if __name__ == "__main__":
    main()

"""Build a fully static, zero-hosting-bill Foundry discovery preview.

This exports only public catalog and preview content. No API keys,
customer PII, email collection, order intake, service activation or checkout.
Hosting is optional; generated files can be reviewed directly on iPhone.
"""
import json
from pathlib import Path

from .commercial_catalog import OFFERS
from .signup_preview import render_signup_preview


READINESS = {
    "mode": "discovery_preview",
    "requires_human_review": True,
    "payment_collection": False,
    "signup_submission": False,
    "live_messaging": False,
    "service_activation": False,
}


def build_static_preview(output_dir: str | Path) -> tuple[Path, ...]:
    """Produce deterministic, dependency-free static files, no network I/O."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    offers = [
        {"slug": offer.slug, "title": offer.title, "status": offer.status,
         "buyer": offer.buyer, "problem": offer.problem,
         "proposed_outcome": offer.proposed_outcome}
        for offer in OFFERS
    ]
    sources = {
        "index.html": render_signup_preview(),
        "offers.json": json.dumps(offers, indent=2, sort_keys=True) + "\n",
        "readiness.json": json.dumps(READINESS, indent=2, sort_keys=True) + "\n",
        "robots.txt": "User-agent: *\nDisallow: /\n",
        ".nojekyll": "",
    }
    generated = []
    for name, content in sources.items():
        path = root / name
        path.write_text(content, encoding="utf-8")
        generated.append(path)
    return tuple(generated)


if __name__ == "__main__":
    generated = build_static_preview("outputs/foundry-static-preview")
    for path in generated:
        print(path)

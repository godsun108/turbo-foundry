"""Generate a truthful, static, customer-facing HTML portfolio with no forms or trackers.

This file is local output. It is not a deployed website or a checkout.
"""
from html import escape
from pathlib import Path

from .commercial_catalog import OFFERS


def render_portfolio() -> str:
    rows = []
    for offer in OFFERS:
        state = "Offline demonstration available" if offer.status == "offline_demo" else "Concept — discovery only"
        rows.append(
            '<article class="offer">'
            f'<p class="status">{escape(state)}</p>'
            f'<h2>{escape(offer.title)}</h2>'
            f'<p>{escape(offer.problem)}</p>'
            f'<p><strong>Proposed approach:</strong> {escape(offer.proposed_outcome)}</p>'
            f'<p><strong>Best fit:</strong> {escape(offer.buyer)}</p>'
            f'<p><strong>Discovery question:</strong> {escape(offer.qualifying_question)}</p>'
            '</article>'
        )
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Foundry Automation | Discovery Portfolio</title>
<style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,sans-serif}
*{box-sizing:border-box}body{margin:0;background:#101820;color:#f3f7fb;line-height:1.55}
main{max-width:1000px;margin:auto;padding:48px 24px}
h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.1;margin:.35em 0}
.lead{max-width:740px;font-size:1.2rem;color:#d6e0e8}
.status{color:#a7e8c0;font-weight:700;text-transform:uppercase;letter-spacing:.04em;font-size:.75rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px;margin-top:32px}
.offer{padding:24px;background:#1b2935;border:1px solid #3f5967;border-radius:18px}
.offer h2{margin-top:.3em}strong{color:#fff}
.note{border-left:4px solid #a7e8c0;padding:12px 20px;background:#1b2935;margin:28px 0}
footer{margin-top:48px;color:#b6c5d0;font-size:.9rem}
</style></head><body><main>
<p class="status">Foundry automation — early discovery</p>
<h1>Less busywork. Better follow-up. Human oversight.</h1>
<p class="lead">We are exploring practical automation solutions for service businesses. Help shape the products by telling us where repetitive work slows your team down.</p>
<div class="note"><strong>Current status:</strong> One missed-call workflow has an offline simulation. The other offerings are concepts. No live integrations, customer messaging, pricing, payment collection, or performance guarantees are available through this page.</div>
<section class="grid" aria-label="Automation ideas">
""" + "\n".join(rows) + """
</section>
<section><h2>What a discovery conversation covers</h2>
<p>We ask about the workflow, current software, staff burden, allowed data access, consent, and outcomes that would justify a pilot. Any live service would require a separate written agreement, security and compliance review, customer approval, and working integration.</p></section>
<footer>Foundry · Exploratory portfolio, not a live service offer or checkout · No customer data is collected by this static page.</footer>
</main></body></html>
"""


def write_portfolio(path: str | Path) -> None:
    Path(path).write_text(render_portfolio(), encoding="utf-8")


if __name__ == "__main__":
    write_portfolio("foundry-portfolio-preview.html")

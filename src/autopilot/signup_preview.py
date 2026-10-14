"""Generate no-network customer onboarding sales funnel PREVIEW.

No personal details leave the browser. No payment processing or deployment.
Do not host as an actual enrollment app without backend security review.
"""
from html import escape
from pathlib import Path

from .commercial_catalog import OFFERS


def render_signup_preview() -> str:
    choices = "".join(
        f'<option value="{escape(o.slug)}">{escape(o.title)}'
        f' — {"Offline demo" if o.status == "offline_demo" else "Concept"}</option>'
        for o in OFFERS
    )
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Foundry | Business onboarding preview</title>
<style>
:root{font-family:system-ui,-apple-system,sans-serif;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:#0f1720;color:#edf6fc}
main{max-width:760px;margin:auto;padding:36px 22px 72px}
h1{font-size:clamp(2rem,5vw,3rem);line-height:1.15}
p{line-height:1.6;color:#c5d6e0}
.card{padding:24px;border-radius:16px;border:1px solid #435967;background:#1b2a36;margin:20px 0}
label{display:block;margin:17px 0 6px;font-weight:650}
input,select,textarea{width:100%;padding:12px;border-radius:8px;background:#11212c;color:#fff;border:1px solid #758a98;font:inherit}
textarea{min-height:82px}button{font:inherit;cursor:pointer;border:0;background:#a9edc7;color:#10241a;padding:14px 20px;border-radius:9px;font-weight:750}
button:disabled{opacity:.55;cursor:not-allowed}
small,.note{color:#afc6d5}.note{border-left:4px solid #a9edc7;padding-left:16px}
</style></head><body><main>
<p class="note"><strong>Prototype only.</strong> No live service, application submission, payment processing, or business enrollment. Information stays in this browser and is not transmitted or stored by this preview.</p>
<h1>Make your business run smoother.</h1>
<p>Tell us what you'd like to improve. This interactive preview shows the future self-service experience. Full-service availability and pricing are not yet approved.</p>
<section class="card"><h2>1. Choose an automation</h2>
<label for="product">Automation idea</label><select id="product">
""" + choices + """</select>
<label for="problem">What needs improvement?</label>
<textarea id="problem" placeholder="e.g. after-hours calls, manual scheduling, follow-up delays"></textarea>
</section>
<section class="card"><h2>2. Business setup</h2>
<label for="business">Business name</label><input id="business" autocomplete="organization" placeholder="Business name">
<label for="industry">Industry</label><input id="industry" placeholder="e.g. plumbing">
<label for="system">Phone / CRM / scheduling system (optional)</label>
<input id="system" placeholder="e.g. current system name">
<label for="goal">What would success look like?</label>
<textarea id="goal" placeholder="e.g. faster response times"></textarea>
</section>
<section class="card"><h2>3. Agreement and review</h2>
<p>Before purchase, the real service would display exact scope, implementation timing, price and billing frequency, refund and cancellation terms, data-processing agreement and customer support details for acceptance.</p>
<p><strong>Next step after an actual verified payment:</strong> restricted onboarding review, provider ownership verification, permissions/consent checks, and operational approval. Payment alone will never automatically start messaging.</p>
<label><input type="checkbox" id="understand" style="width:auto"> I understand this is an offline prototype and no order will be placed.</label>
<button type="button" id="preview">Preview my setup summary</button>
<div id="output" role="status" aria-live="polite"></div>
</section>
<section class="card"><h2>4. Secure checkout</h2>
<p>Once approved for sale, payment will be collected using hosted Stripe Checkout. We never ask for payment card numbers in this form.</p>
<button type="button" disabled aria-disabled="true">Checkout — not yet available</button>
</section>
<p><small>Foundry sales funnel prototype · No tracking, network requests, cookies or local storage</small></p>
</main><script>
(() => {
  const val = id => document.getElementById(id).value.trim();
  const out = document.getElementById('output');
  document.getElementById('preview').addEventListener('click', () => {
    out.replaceChildren();
    if (!document.getElementById('understand').checked) {
      out.textContent = 'Please confirm you understand the preview limitations.';
      return;
    }
    const business=val('business'), problem=val('problem');
    if (!business || !problem) {
      out.textContent = 'Please enter a business name and the problem to solve.';
      return;
    }
    const heading=document.createElement('h3');
    heading.textContent='Your offline setup summary';
    out.appendChild(heading);
    [
      ['Business',business],['Automation',document.getElementById('product').selectedOptions[0].textContent],
      ['Problem',problem],['Industry',val('industry')||'Not provided'],
      ['Current systems',val('system')||'Not provided'],
      ['Goal',val('goal')||'Not provided']
    ].forEach(([key,value]) => {
      const p=document.createElement('p');
      p.textContent=key+': '+value;
      out.appendChild(p);
    });
    const note=document.createElement('p');
    note.textContent='NOT SUBMITTED. No payment requested or service activated.';
    out.appendChild(note);
  });
})();
</script></body></html>"""


def write_signup_preview(path: str | Path):
    Path(path).write_text(render_signup_preview(), encoding="utf-8")


if __name__ == "__main__":
    write_signup_preview("foundry-onboarding-preview.html")

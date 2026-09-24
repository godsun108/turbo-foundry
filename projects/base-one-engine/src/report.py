"""Standardized, non-prescriptive Base One deal report."""
from __future__ import annotations
from intake import PropertyRecord, Source, make_deal_record
from scenario import FinancingScenario, compare_scenarios, stress_test

REQUIRED_ANALYSIS_FIELDS=(
    "annual_property_tax","annual_insurance_estimate",
    "monthly_rent_estimate","rehab_estimate",
)

def missing_fields(p:PropertyRecord)->list[str]:
    return [f for f in REQUIRED_ANALYSIS_FIELDS if getattr(p,f) is None]

def build_deal_report(p:PropertyRecord,sources:list[Source],
                      scenarios:list[FinancingScenario],
                      vacancy_rate:float=0.05,
                      other_monthly_operating_expenses:float=0.0)->dict:
    """Build a reproducible report without issuing a buy/sell verdict."""
    record=make_deal_record(
        p,sources,
        {"vacancy_rate":vacancy_rate,
         "other_monthly_operating_expenses":other_monthly_operating_expenses},
    )
    missing=missing_fields(p)
    report={
        "report_version":"base-one-report-v0.1",
        "record_sha256":record["record_sha256"],
        "property":record["property"],
        "sources":record["sources"],
        "assumptions":record["assumptions"],
        "missing_fields":missing,
        "analysis_status":"incomplete" if missing else "complete",
        "scenario_results":[],
        "stress_results":{},
    }
    if missing:
        return report

    monthly_fixed=(p.annual_property_tax+p.annual_insurance_estimate)/12
    prop={
        "purchase_price":p.asking_price,
        "monthly_rent":p.monthly_rent_estimate,
        "monthly_operating_expenses":monthly_fixed+other_monthly_operating_expenses,
        "vacancy_rate":vacancy_rate,
    }
    report["scenario_results"]=compare_scenarios(prop,scenarios)
    for s in scenarios:
        report["stress_results"][s.name]=stress_test(prop,s)
    return report

def render_markdown(r:dict)->str:
    p=r["property"]
    lines=[
        "# Base One Deal Report",
        "",
        f"**Property:** {p['address']}",
        f"**Asking price:** ${p['asking_price']:,.2f}",
        f"**Analysis status:** {r['analysis_status'].upper()}",
        f"**Record fingerprint:** `{r['record_sha256']}`",
        "",
    ]
    if r["missing_fields"]:
        lines += ["## Missing data",""]+[f"- {x}" for x in r["missing_fields"]]
        lines += ["","Financial scenario calculations are withheld until required inputs are supplied."]
        return "\n".join(lines)+"\n"

    lines += ["## Scenario comparison","",
              "| Scenario | Cash required | Monthly cash flow | Cap rate | Cash-on-cash |",
              "|---|---:|---:|---:|---:|"]
    for x in r["scenario_results"]:
        coc=x["cash_on_cash_return"]
        coc_text="n/a" if coc is None else f"{coc:.2%}"
        lines.append(f"| {x['financing']['name']} | ${x['cash_required']:,.2f} | ${x['monthly_cash_flow']:,.2f} | {x['cap_rate']:.2%} | {coc_text} |")
    lines += ["","## Provenance",""]
    for s in r["sources"]:
        lines.append(f"- {s['kind']}: {s['reference']} (retrieved {s['retrieved_at']})")
    lines += ["","## Interpretation","",
              "This report presents calculations under stated assumptions. It does not issue a buy/sell recommendation, appraisal, lending decision, legal opinion, or tax opinion."]
    return "\n".join(lines)+"\n"

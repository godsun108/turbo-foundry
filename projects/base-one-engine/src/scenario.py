"""Scenario and stress-test layer for Base One Engine."""
from dataclasses import dataclass, asdict
from itertools import product
from deal import DealInputs, analyze

@dataclass(frozen=True)
class FinancingScenario:
    name: str
    down_payment: float
    closing_costs: float
    rehab: float
    monthly_debt_service: float
    notes: str = ""

def analyze_scenario(*, purchase_price:float, monthly_rent:float,
                     monthly_operating_expenses:float, vacancy_rate:float,
                     financing:FinancingScenario)->dict:
    base=DealInputs(
        purchase_price=purchase_price,
        down_payment=financing.down_payment,
        closing_costs=financing.closing_costs,
        rehab=financing.rehab,
        monthly_rent=monthly_rent,
        monthly_operating_expenses=monthly_operating_expenses,
        monthly_debt_service=financing.monthly_debt_service,
        vacancy_rate=vacancy_rate,
    )
    out=analyze(base)
    out["financing"]=asdict(financing)
    return out

def compare_scenarios(property_inputs:dict, scenarios:list[FinancingScenario])->list[dict]:
    if not scenarios:
        raise ValueError("at least one financing scenario is required")
    return [analyze_scenario(financing=s,**property_inputs) for s in scenarios]

def stress_test(property_inputs:dict, financing:FinancingScenario,
                rent_multipliers=(0.9,1.0,1.1),
                vacancy_rates=(0.05,0.10,0.15),
                expense_multipliers=(1.0,1.15,1.30))->list[dict]:
    rows=[]
    for rm,vac,em in product(rent_multipliers,vacancy_rates,expense_multipliers):
        p=dict(property_inputs)
        p["monthly_rent"]=property_inputs["monthly_rent"]*rm
        p["monthly_operating_expenses"]=property_inputs["monthly_operating_expenses"]*em
        p["vacancy_rate"]=vac
        r=analyze_scenario(financing=financing,**p)
        rows.append({
            "rent_multiplier":rm,
            "vacancy_rate":vac,
            "expense_multiplier":em,
            "monthly_cash_flow":r["monthly_cash_flow"],
            "annual_noi":r["annual_noi"],
            "cash_on_cash_return":r["cash_on_cash_return"],
            "break_even_occupancy":r["break_even_occupancy"],
        })
    return rows

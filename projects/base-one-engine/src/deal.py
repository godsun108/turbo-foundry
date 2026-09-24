"""Deterministic Base One property-deal calculations."""
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass(frozen=True)
class DealInputs:
    purchase_price: float
    down_payment: float
    closing_costs: float
    rehab: float
    monthly_rent: float
    monthly_operating_expenses: float
    monthly_debt_service: float
    vacancy_rate: float = 0.05

    def validate(self):
        money=(self.purchase_price,self.down_payment,self.closing_costs,self.rehab,
               self.monthly_rent,self.monthly_operating_expenses,self.monthly_debt_service)
        if any(x < 0 for x in money):
            raise ValueError("money inputs cannot be negative")
        if not 0 <= self.vacancy_rate <= 1:
            raise ValueError("vacancy_rate must be between 0 and 1")
        if self.purchase_price <= 0:
            raise ValueError("purchase_price must be positive")

def analyze(x: DealInputs) -> dict:
    x.validate()
    effective_rent=x.monthly_rent*(1-x.vacancy_rate)
    monthly_noi=effective_rent-x.monthly_operating_expenses
    monthly_cash_flow=monthly_noi-x.monthly_debt_service
    annual_noi=monthly_noi*12
    cash_required=x.down_payment+x.closing_costs+x.rehab
    cap_rate=annual_noi/x.purchase_price
    cash_on_cash=(monthly_cash_flow*12/cash_required) if cash_required>0 else None
    break_even=((x.monthly_operating_expenses+x.monthly_debt_service)/x.monthly_rent
                if x.monthly_rent>0 else None)
    return {
        "inputs":asdict(x),
        "effective_monthly_rent":effective_rent,
        "monthly_noi":monthly_noi,
        "annual_noi":annual_noi,
        "monthly_cash_flow":monthly_cash_flow,
        "cash_required":cash_required,
        "cap_rate":cap_rate,
        "cash_on_cash_return":cash_on_cash,
        "break_even_occupancy":break_even,
    }

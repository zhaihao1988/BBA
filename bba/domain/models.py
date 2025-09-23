from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List


@dataclass(frozen=True)
class PolicyLite:
    policy_no: str
    class_code: str
    start_date: date
    end_date: date
    sum_premium_no_tax: Decimal


@dataclass(frozen=True)
class AssumptionLite:
    year: int
    class_code: str
    discount_rate: float
    claims_rate: float
    claim_expense_rate: float
    maintenance_cost_rate: float
    expected_acquisition_cost_rate: float


@dataclass(frozen=True)
class CurvePoint:
    tenor_years: float
    rate: float


@dataclass
class CashFlowSeries:
    periods: List[int]
    premium: List[float]
    claims: List[float]
    expenses: List[float]
    discount_factors: List[float]



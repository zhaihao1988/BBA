from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List, Optional
import pandas as pd


@dataclass(frozen=True)
class PolicyRecord:
    policy_no: str
    class_code: str
    start_date: date
    end_date: date
    sum_premium_no_tax: Decimal

    @staticmethod
    def from_row(row: Dict[str, Any]) -> "PolicyRecord":
        return PolicyRecord(
            policy_no=str(row["policy_no"]),
            class_code=str(row["class_code"]),
            start_date=pd.to_datetime(row["start_date"]).date(),
            end_date=pd.to_datetime(row["end_date"]).date(),
            sum_premium_no_tax=Decimal(str(row["sum_premium_no_tax"])) if pd.notna(row["sum_premium_no_tax"]) else Decimal("0"),
        )


@dataclass(frozen=True)
class AssumptionRecord:
    year: int
    class_code: str
    discount_rate: float
    expected_acquisition_cost_rate: float
    claims_rate: float
    claim_expense_rate: float
    maintenance_cost_rate: float
    non_financial_risk_adjustment: float

    @staticmethod
    def from_row(row: Dict[str, Any]) -> "AssumptionRecord":
        return AssumptionRecord(
            year=int(row["年份"]),
            class_code=str(row["险种大类"]).zfill(6),
            discount_rate=float(row["利率"]),
            expected_acquisition_cost_rate=float(row["获取费用率"]),
            claims_rate=float(row["赔付率"]),
            claim_expense_rate=float(row["间接理赔费用率"]),
            maintenance_cost_rate=float(row["维持费用率"]),
            non_financial_risk_adjustment=float(row["未到期边际"]),
        )


@dataclass(frozen=True)
class CurveRecord:
    name: str
    as_of: date
    rates: Dict[str, float]

    @staticmethod
    def from_row(row: Dict[str, Any]) -> "CurveRecord":
        return CurveRecord(
            name=str(row["曲线名称"]),
            as_of=pd.to_datetime(row["日期"]).date(),
            rates={
                "3M": float(row["3月"]),
                "6M": float(row["6月"]),
                "1Y": float(row["1年"]),
                "3Y": float(row["3年"]),
                "5Y": float(row["5年"]),
                "7Y": float(row["7年"]),
                "10Y": float(row["10年"]),
                "30Y": float(row["30年"]),
            },
        )


@dataclass(frozen=True)
class VoucherRecord:
    policy_no: str
    subject_code: str
    subject_name: Optional[str]
    amount: Decimal

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "VoucherRecord":
        return VoucherRecord(
            policy_no=str(d["保单号"]),
            subject_code=str(d["科目代码"]),
            subject_name=str(d.get("科目名称") or ""),
            amount=Decimal(str(d["金额"])) if d.get("金额") is not None else Decimal("0"),
        )



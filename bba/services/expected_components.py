from __future__ import annotations

from datetime import datetime
import pandas as pd


def calculate_claim_expense(policy, assumption, data: pd.DataFrame, end_of_year: datetime) -> float:
    claim_expense_rate = assumption.claim_expense_rate * assumption.claims_rate
    if policy.warranty_date.year > end_of_year.year:
        return 0.0
    elif policy.warranty_date.year == end_of_year.year:
        return float(
            data.loc["预期保费流入", "总计"]
            * claim_expense_rate
            * ((end_of_year - policy.warranty_date).days + 1)
            / ((policy.end_date - policy.warranty_date).days + 1)
        )
    else:
        return float(
            data.loc["预期保费流入", "总计"]
            * claim_expense_rate
            * data.loc["经过时间", end_of_year]
            / ((policy.end_date - policy.warranty_date).days + 1)
        )


def calculate_maintenance_cost(policy, assumption, data: pd.DataFrame, end_of_year: datetime) -> float:
    if policy.warranty_date.year > end_of_year.year:
        return 0.0
    elif policy.warranty_date.year == end_of_year.year:
        return float(
            data.loc["预期保费流入", "总计"]
            * assumption.maintenance_cost_rate
            * ((end_of_year - policy.warranty_date).days + 1)
            / ((policy.end_date - policy.warranty_date).days + 1)
        )
    else:
        return float(
            data.loc["预期保费流入", "总计"]
            * assumption.maintenance_cost_rate
            * data.loc["经过时间", end_of_year]
            / ((policy.end_date - policy.warranty_date).days + 1)
        )


def calculate_non_financial_risk(policy, assumption, data: pd.DataFrame, end_of_year: datetime) -> float:
    ra_rate = (
        (assumption.claims_rate + assumption.maintenance_cost_rate + assumption.claims_rate * assumption.claim_expense_rate)
        * assumption.non_financial_risk_adjustment
    )
    if policy.warranty_date.year > end_of_year.year:
        return 0.0
    elif policy.warranty_date.year == end_of_year.year:
        return float(
            data.loc["预期保费流入", "总计"]
            * ra_rate
            * ((end_of_year - policy.warranty_date).days + 1)
            / ((policy.end_date - policy.warranty_date).days + 1)
        )
    else:
        return float(
            data.loc["预期保费流入", "总计"]
            * ra_rate
            * data.loc["经过时间", end_of_year]
            / ((policy.end_date - policy.warranty_date).days + 1)
        )


def calculate_expected_claims(policy, assumption, data: pd.DataFrame, end_of_year: datetime) -> float:
    if policy.warranty_date.year > end_of_year.year:
        return 0.0
    elif policy.warranty_date.year == end_of_year.year:
        return float(
            data.loc["预期保费流入", "总计"]
            * assumption.claims_rate
            * ((end_of_year - policy.warranty_date).days + 1)
            / ((policy.end_date - policy.warranty_date).days + 1)
        )
    else:
        return float(
            data.loc["预期保费流入", "总计"]
            * assumption.claims_rate
            * data.loc["经过时间", end_of_year]
            / ((policy.end_date - policy.warranty_date).days + 1)
        )



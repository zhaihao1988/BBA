from __future__ import annotations

from typing import Iterable, Tuple
import pandas as pd
from pandas import Timestamp
from bba.domain.models import CashFlowSeries
from 国债收益率 import InterestRateCurve


class DiscountService:
    def apply(self, series: CashFlowSeries, curve: InterestRateCurve) -> CashFlowSeries:
        # 占位实现：保持目录结构，后续将贴现逻辑迁移自 ExpectedCashFlow
        return series


def compute_discounted_data(
    data: pd.DataFrame,
    policy_start_date: Timestamp,
    assumption_discount_rate: float,
    date: Timestamp,
) -> Tuple[float, float, float, float]:
    """等价于 ExpectedCashFlow.compute_discounted_data 的核心计算。

    返回: (非金融部分折现值合计, 全部折现值合计, RA折现值合计(未折现), 获取费用折现值合计)
    """
    total_discounted_value_for_non_financial = 0.0
    total_discounted_value = 0.0
    total_ra_discounted_value = 0.0
    total_acquisition_discounted_value = 0.0

    date = pd.to_datetime(date)

    columns_to_process = [col for col in data.columns if col not in ["总计", "折现值"]]

    valid_columns = []
    for col in columns_to_process:
        try:
            valid_columns.append(pd.to_datetime(col))
        except ValueError:
            continue

    columns_to_process = [col for col in valid_columns if col >= date]

    rows_to_process = [
        "预期保费流入",
        "预期赔付支出",
        "预期获取费用",
        "预期间接理赔费用",
        "预期维持费用",
        "非金融风险",
    ]

    for row in rows_to_process:
        if row in data.index:
            for col in columns_to_process:
                discount_factor_for_non_financial = data.loc["调整前折现因子", col] * (
                    1 + data.loc["调整前折现率", date.replace(date.year - 1, 12, 31, 23, 59, 59)]
                ) ** ((date - policy_start_date).days / 365)

                discount_factor = data.loc["折现因子", col] * (
                    1 + data.loc["折现率", date.replace(date.year - 1, 12, 31, 23, 59, 59)]
                ) ** ((date - policy_start_date).days / 365)

                if row == "预期保费流入":
                    current_value = (-1) * data.loc[row, col]
                else:
                    current_value = data.loc[row, col]

                discounted_value_for_non_financial = current_value * discount_factor_for_non_financial
                discount_value = current_value * discount_factor

                if row == "非金融风险":
                    total_ra_discounted_value += current_value
                else:
                    total_discounted_value_for_non_financial += discounted_value_for_non_financial
                    total_discounted_value += discount_value

                if row == "预期获取费用":
                    total_acquisition_discounted_value += discounted_value_for_non_financial

    return (
        float(total_discounted_value_for_non_financial),
        float(total_discounted_value),
        float(total_ra_discounted_value),
        float(total_acquisition_discounted_value),
    )



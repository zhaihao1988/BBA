from __future__ import annotations

from typing import List
import pandas as pd
from bba.domain.models import CashFlowSeries, PolicyLite, AssumptionLite


class CashFlowCalculator:
    def build_series(self, policy: PolicyLite, assumption: AssumptionLite) -> CashFlowSeries:
        # 占位实现：保持目录结构，后续可将现有 ExpectedCashFlow 逻辑迁移至此
        return CashFlowSeries(periods=[], premium=[], claims=[], expenses=[], discount_factors=[])

    @staticmethod
    def build_series_from_expected_df(df: pd.DataFrame) -> CashFlowSeries:
        """从 ExpectedCashFlow.data DataFrame 构建结构化序列。

        仅读取列为日期的部分，按升序输出对应行的数值列表。
        """
        columns_to_sort = [col for col in df.columns if col not in ["总计", "折现值"]]
        sorted_columns = sorted(columns_to_sort)
        periods = list(range(1, len(sorted_columns) + 1))
        premium = [float(df.loc["预期保费流入", c]) for c in sorted_columns]
        claims = [float(df.loc["预期赔付支出", c]) for c in sorted_columns]
        expenses = [
            float(df.loc["预期获取费用", c] + df.loc["预期间接理赔费用", c] + df.loc["预期维持费用", c])
            for c in sorted_columns
        ]
        discount_factors = [float(df.loc["折现因子", c]) for c in sorted_columns]
        return CashFlowSeries(periods=periods, premium=premium, claims=claims, expenses=expenses, discount_factors=discount_factors)



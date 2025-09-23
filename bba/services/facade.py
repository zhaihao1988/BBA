from __future__ import annotations

from typing import Tuple, List, Dict, Any
import pandas as pd

from 预期现金流 import ExpectedCashFlow
from 实际现金流 import ActualCashFlow


def compute_policy_metrics(policy,
                           policies,
                           assumptions,
                           curves,
                           vouchers,
                           cost_allocations) -> Tuple[Dict[str, Any], List[Any]]:
    # 与现有用例一致的流程，后续可逐步迁移具体计算到 bba/services
    policy.expected_cash_flow = ExpectedCashFlow(policy, policies, assumptions, curves)
    policy.expected_cash_flow.compute_data(policies)
    policy.actual_cash_flow = ActualCashFlow(policy, vouchers, cost_allocations)
    policy.actual_cash_flow.compute_data()
    policy.generate_lrc_units()

    metrics = {
        "policy_no": policy.policy_no,
        "bel": policy.bel_2023,
        "yi_fa_sheng": policy.yi_fa_sheng_2023,
        "ra": policy.ra_2023,
        "csm": policy.csm_2023,
        "sum": policy.lrc_2023,
        "acquisition_balance": policy.acquisition_2023,
        "bel_start": policy.bel_start,
        "ra_start": policy.ra_start,
        "csm_start": policy.csm_start,
    }
    return metrics, policy.voucher_gens



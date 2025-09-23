from __future__ import annotations

import os
import pandas as pd
from bba.app.usecases import run_single_policy


def compare_single_policy(policy_no: str, baseline_path: str, **paths):
    result = run_single_policy(policy_no=policy_no, **paths)
    out_path = result["summary_path"]
    base = pd.read_excel(baseline_path)
    new = pd.read_excel(out_path)
    # 仅比较关键列
    cols = [
        "policy.bel",
        "policy.yi_fa_sheng",
        "policy.ra",
        "policy.csm",
        "policy.sum",
        "policy.acquisition_balance",
        "policy.bel_start",
        "policy.ra_start",
        "policy.csm_start",
    ]
    diff = (new[cols] - base[cols]).abs().sum().sum()
    return diff, out_path



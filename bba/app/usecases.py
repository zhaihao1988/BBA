import os
from typing import Optional, List, Dict, Any, Tuple
import pandas as pd
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

from bba.infrastructure.excel_repositories import (
    PolicyRepository,
    AssumptionRepository,
    CurveRepository,
    VoucherRepository,
    CostAllocationRepository,
)

from bba.infrastructure.config_loader import load_chart_of_accounts
from bba.adapters.dataframe_adapter import save_expected_cash_flow, save_actual_cash_flow, save_lrc_units
from bba.services.facade import compute_policy_metrics


def _ensure_out_dir() -> str:
    out_dir = os.path.join(os.getcwd(), "out")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def run_single_policy(policy_no: str,
                      policy_path: str,
                      assumptions_path: str,
                      curves_path: str,
                      vouchers_path: str,
                      cost_allocation_path: str,
                      coa_path: str = "bba/config/chart_of_accounts.yml") -> Dict[str, Any]:
    policies = PolicyRepository(policy_path).load()
    assumptions = AssumptionRepository(assumptions_path).load()
    curves = CurveRepository(curves_path).load()
    vouchers = VoucherRepository(vouchers_path).load()
    cost_allocations = CostAllocationRepository(cost_allocation_path).load()

    # 找到目标保单（与原逻辑相同条件：certi_no 为空）
    target = next((p for p in policies if str(p.policy_no) == str(policy_no) and pd.isna(p.certi_no)), None)
    if target is None:
        raise ValueError(f"未找到保单: {policy_no}")

    metrics, voucher_list = compute_policy_metrics(target, policies, assumptions, curves, vouchers, cost_allocations)
    # 科目名称补全/校验
    coa = load_chart_of_accounts(coa_path)
    for v in voucher_list:
        if not v.subject_name or v.subject_name == '未知科目':
            v.subject_name = coa.get(str(v.subject_code), v.subject_name)

    out_dir = _ensure_out_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 导出明细
    save_expected_cash_flow(target.policy_no, target.expected_cash_flow.data, out_dir, ts)
    save_actual_cash_flow(target.policy_no, target.actual_cash_flow.data, out_dir, ts)
    # 导出每年度 104 表（LRCUnit values 矩阵），每个年度一个 sheet
    lrc_units_path = None
    if getattr(target, 'lrc_units', None):
        lrc_units_path = save_lrc_units(target.policy_no, target.lrc_units, out_dir, ts)

    # 导出核心汇总
    confirm_data = {
        "policy_no": [target.policy_no],
        "policy.bel": [target.bel_2023],
        "policy.yi_fa_sheng": [target.yi_fa_sheng_2023],
        "policy.ra": [target.ra_2023],
        "policy.csm": [target.csm_2023],
        "policy.sum": [target.lrc_2023],
        "policy.acquisition_balance": [target.acquisition_2023],
        "policy.bel_start": [target.bel_start],
        "policy.ra_start": [target.ra_start],
        "policy.csm_start": [target.csm_start],
    }
    pd.DataFrame(confirm_data).to_excel(os.path.join(out_dir, f"single_policy_{policy_no}_{ts}.xlsx"), index=False)

    # 导出凭证
    voucher_rows = [{
        "凭证ID": v.voucher_id,
        "保单号": v.policy_number,
        "科目代码": v.subject_code,
        "科目名称": v.subject_name,
        "金额": v.amount,
    } for v in target.voucher_gens]
    pd.DataFrame(voucher_rows).to_excel(os.path.join(out_dir, f"vouchers_{policy_no}_{ts}.xlsx"), index=False)

    return {
        "policy_no": policy_no,
        "summary_path": os.path.join(out_dir, f"single_policy_{policy_no}_{ts}.xlsx"),
        "vouchers_path": os.path.join(out_dir, f"vouchers_{policy_no}_{ts}.xlsx"),
        "lrc_units_path": lrc_units_path,
    }


def _run_single_for_pool(args: Tuple[Any, List[Any], List[Any], List[Any], List[Any]]):
    p, policies, assumptions, curves, vouchers, cost_allocations = args
    # 计算并返回必要指标与凭证
    from bba.services.facade import compute_policy_metrics
    metrics, voucher_list = compute_policy_metrics(p, policies, assumptions, curves, vouchers, cost_allocations)
    return (
        p.policy_no,
        p.lrc_2023, p.bel_2023, p.csm_2023, p.ra_2023, p.end_balance, p.csm_start, p.yi_fa_sheng_2023,
        metrics,
        voucher_list,
    )


def run_full_batch(policy_path: str,
                   assumptions_path: str,
                   curves_path: str,
                   vouchers_path: str,
                   cost_allocation_path: str,
                   coa_path: str = "bba/config/chart_of_accounts.yml",
                   workers: int = 1) -> Dict[str, Any]:
    policies = PolicyRepository(policy_path).load()
    assumptions = AssumptionRepository(assumptions_path).load()
    curves = CurveRepository(curves_path).load()
    vouchers = VoucherRepository(vouchers_path).load()
    cost_allocations = CostAllocationRepository(cost_allocation_path).load()

    LRC_sum = bel_sum = csm_sum = ra_sum = balance_sum = csm_start_sum = yi_fa_sheng_sum = 0
    confirm_data = {k: [] for k in [
        "policy_no","policy.bel","policy.yi_fa_sheng","policy.ra","policy.csm","policy.sum",
        "policy.acquisition_balance","policy.bel_start","policy.ra_start","policy.csm_start"
    ]}
    voucher_gens = []
    coa = load_chart_of_accounts(coa_path)

    eligible = [p for p in policies if pd.isna(p.certi_no)]

    if workers <= 1:
        # 串行
        for p in eligible:
            metrics, voucher_list = compute_policy_metrics(p, policies, assumptions, curves, vouchers, cost_allocations)
            for v in p.voucher_gens:
                if not v.subject_name or v.subject_name == '未知科目':
                    v.subject_name = coa.get(str(v.subject_code), v.subject_name)
            LRC_sum += p.lrc_2023; bel_sum += p.bel_2023; csm_sum += p.csm_2023; ra_sum += p.ra_2023
            balance_sum += p.end_balance; csm_start_sum += p.csm_start; yi_fa_sheng_sum += p.yi_fa_sheng_2023
            voucher_gens.extend(voucher_list)
            confirm_data["policy_no"].append(p.policy_no)
            confirm_data["policy.bel"].append(p.bel_2023)
            confirm_data["policy.yi_fa_sheng"].append(p.yi_fa_sheng_2023)
            confirm_data["policy.ra"].append(p.ra_2023)
            confirm_data["policy.csm"].append(p.csm_2023)
            confirm_data["policy.sum"].append(p.lrc_2023)
            confirm_data["policy.acquisition_balance"].append(p.acquisition_2023)
            confirm_data["policy.bel_start"].append(p.bel_start)
            confirm_data["policy.ra_start"].append(p.ra_start)
            confirm_data["policy.csm_start"].append(p.csm_start)
    else:
        # 并行（进程池）
        tasks = [
            (p, policies, assumptions, curves, vouchers, cost_allocations)
            for p in eligible
        ]
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(_run_single_for_pool, t) for t in tasks]
            for fut in as_completed(futures):
                policy_no, lrc_2023, bel_2023, csm_2023, ra_2023, end_balance, csm_start, yi_fa_sheng, metrics, voucher_list = fut.result()
                # 补科目名称
                for v in voucher_list:
                    if not v.subject_name or v.subject_name == '未知科目':
                        v.subject_name = coa.get(str(v.subject_code), v.subject_name)
                LRC_sum += lrc_2023; bel_sum += bel_2023; csm_sum += csm_2023; ra_sum += ra_2023
                balance_sum += end_balance; csm_start_sum += csm_start; yi_fa_sheng_sum += yi_fa_sheng
                voucher_gens.extend(voucher_list)
                confirm_data["policy_no"].append(policy_no)
                confirm_data["policy.bel"].append(bel_2023)
                confirm_data["policy.yi_fa_sheng"].append(yi_fa_sheng)
                confirm_data["policy.ra"].append(ra_2023)
                confirm_data["policy.csm"].append(csm_2023)
                confirm_data["policy.sum"].append(lrc_2023)
                # acquisition_balance 无法从池返回的 p 取，保留为空或后续补
                confirm_data["policy.acquisition_balance"].append(None)
                confirm_data["policy.bel_start"].append(None)
                confirm_data["policy.ra_start"].append(None)
                confirm_data["policy.csm_start"].append(None)

    out_dir = _ensure_out_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = os.path.join(out_dir, f"batch_summary_{ts}.xlsx")
    voucher_path = os.path.join(out_dir, f"batch_vouchers_{ts}.xlsx")

    pd.DataFrame(confirm_data).to_excel(summary_path, index=False)
    pd.DataFrame([{
        "凭证ID": v.voucher_id,
        "保单号": v.policy_number,
        "科目代码": v.subject_code,
        "科目名称": v.subject_name,
        "金额": v.amount,
    } for v in voucher_gens]).to_excel(voucher_path, index=False)

    totals = {
        "LRC_sum": LRC_sum,
        "bel_sum": bel_sum,
        "yi_fa_sheng_sum": yi_fa_sheng_sum,
        "csm_sum": csm_sum,
        "ra_sum": ra_sum,
        "balance_sum": balance_sum,
        "csm_start_sum": csm_start_sum,
    }
    pd.DataFrame([totals]).to_excel(os.path.join(out_dir, f"batch_totals_{ts}.xlsx"), index=False)

    return {"summary_path": summary_path, "voucher_path": voucher_path, "totals": totals}



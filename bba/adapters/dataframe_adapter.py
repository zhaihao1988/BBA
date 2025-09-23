import os
from typing import Optional, List
import pandas as pd


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_expected_cash_flow(policy_no: str, df: pd.DataFrame, out_dir: str, ts: str) -> str:
    _ensure_dir(out_dir)
    path = os.path.join(out_dir, f"expected_cash_flow_{policy_no}_{ts}.xlsx")
    df.to_excel(path, index=True)
    return path


def save_actual_cash_flow(policy_no: str, df: pd.DataFrame, out_dir: str, ts: str) -> str:
    _ensure_dir(out_dir)
    path = os.path.join(out_dir, f"actual_cash_flow_{policy_no}_{ts}.xlsx")
    df.to_excel(path, index=True)
    return path


def save_lrc_units(policy_no: str, lrc_units: List, out_dir: str, ts: str) -> str:
    _ensure_dir(out_dir)
    path = os.path.join(out_dir, f"lrc_units_{policy_no}_{ts}.xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for unit in lrc_units:
            sheet_name = str(unit.year)
            unit.data.to_excel(writer, sheet_name=sheet_name, index=True)
    return path



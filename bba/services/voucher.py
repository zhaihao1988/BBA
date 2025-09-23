from __future__ import annotations

from typing import List, Dict
from 生成会计凭证 import VoucherGen
from bba.infrastructure.config_loader import load_chart_of_accounts


class VoucherGenerator:
    def __init__(self, coa_path: str = "bba/config/chart_of_accounts.yml"):
        self._coa: Dict[str, str] = load_chart_of_accounts(coa_path)

    def generate(self, policy_no: str, entries: List[tuple[str, float]]) -> List[VoucherGen]:
        vouchers: List[VoucherGen] = []
        for subject_code, amount in entries:
            vg = VoucherGen(policy_no, subject_code, amount)
            # 名称补全
            if not vg.subject_name or vg.subject_name == '未知科目':
                vg.subject_name = self._coa.get(str(subject_code), vg.subject_name)
            vouchers.append(vg)
        return vouchers



import os
from typing import List
import pandas as pd

# 直接复用现有领域类，保持逻辑一致
from 保单处理 import Policy, filter_policies
from 收付凭证 import Voucher
from 精算假设 import ActuarialAssumptions
from 国债收益率 import InterestRateCurve
from 费用分摊 import CostAllocation


class PolicyRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Policy]:
        df = pd.read_excel(self.file_path, sheet_name="Sheet1", dtype={'class_code': str})
        policies: List[Policy] = []
        for _, row in df.iterrows():
            policy = Policy(
                id=row['id'],
                bi_id=row['bi_id'],
                policy_no=row['policy_no'],
                certi_no=row['certi_no'],
                class_code=row['class_code'],
                risk_code=row['risk_code'],
                com_code=row['com_code'],
                business_nature=row['business_nature'],
                channel_type=row['channel_type'],
                app_li_type=row['app_li_type'],
                customer_group=row['customer_group'],
                center_code=row['center_code'],
                segment1=row['segment1'],
                segment2=row['segment2'],
                segment6=row['segment6'],
                segment7=row['segment7'],
                segment8=row['segment8'],
                app_li_code=row['app_li_code'],
                car_kind_code=row['car_kind_code'],
                use_nature_code=row['use_nature_code'],
                business_type=row['business_type'],
                coins_flag=row['coins_flag'],
                present_flag=row['present_flag'],
                card_flag=row['card_flag'],
                d_fee_flag=row['d_fee_flag'],
                under_write_date=row['under_write_date'],
                first_plan_end_date=row['first_plan_end_date'],
                return_flag=row['return_flag'],
                max_pay_rate=row['max_pay_rate'],
                min_pay_rate=row['min_pay_rate'],
                start_date=row['start_date'],
                end_date=row['end_date'],
                valid_date=row['valid_date'],
                loss_ratio_init=row['loss_ratio_init'],
                loss_ratio_agr=row['loss_ratio_agr'],
                modify_type=row['modify_type'],
                revise_flag=row['revise_flag'],
                amount_limit=row['amount_limit'],
                plan_revise_flag=row['plan_revise_flag'],
                pay_no=row['pay_no'],
                plan_date=row['plan_date'],
                sum_premium_no_tax=row['sum_premium_no_tax'],
                currency=row['currency'],
                stat_date=row['stat_date'],
                create_time=row['create_time'],
                last_update_time=row['last_update_time'],
                create_user=row['create_user'],
                warranty=row['warranty'],
                premium_date=row['premium_date']
            )
            policies.append(policy)
        # 复用现有过滤逻辑
        return filter_policies(policies)


class AssumptionRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[ActuarialAssumptions]:
        df = pd.read_excel(self.file_path, sheet_name="Assumptions", dtype={'险种大类': str})
        assumptions: List[ActuarialAssumptions] = []
        for _, row in df.iterrows():
            assumption = ActuarialAssumptions(
                year=row['年份'],
                class_code=row['险种大类'],
                claims_rate=row['赔付率'],
                maintenance_cost_rate=row['维持费用率'],
                claim_expense_rate=row['间接理赔费用率'],
                expected_acquisition_cost_rate=row['获取费用率'],
                non_financial_risk_adjustment=row['未到期边际'],
                discount_rate=row['利率']
            )
            assumptions.append(assumption)
        return assumptions


class CurveRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[InterestRateCurve]:
        df = pd.read_excel(self.file_path)
        curves: List[InterestRateCurve] = []
        for _, row in df.iterrows():
            name = row['曲线名称']
            date = row['日期']
            rates = {
                "3M": row['3月'], "6M": row['6月'], "1Y": row['1年'],
                "3Y": row['3年'], "5Y": row['5年'], "7Y": row['7年'],
                "10Y": row['10年'], "30Y": row['30年']
            }
            curves.append(InterestRateCurve(name, date, rates))
        return curves


class VoucherRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Voucher]:
        df = pd.read_excel(self.file_path, sheet_name="收付系统")
        vouchers: List[Voucher] = []
        for _, row in df.iterrows():
            voucher = Voucher(
                voucher_number=row['压缩凭证号'],
                voucher_sequence=row['凭证序号'],
                debit_credit_direction=row['借贷方向'],
                accounting_subject=row['会计科目'],
                accounting_name=row['会计名称'],
                voucher_date=row['凭证日期'],
                original_currency_amount=row['原币金额'],
                local_currency_amount=row['本币金额'],
                debit_credit=row['借-贷'],
                local_currency_code=row['本币币种代码'],
                exchange_rate=row['汇率'],
                accounting_type=row['做账类型'],
                business_type=row['业务类型'],
                issuing_institution=row['出单机构'],
                accounting_institution=row['做账机构'],
                company_segment=row['公司段'],
                cost_center=row['成本中心'],
                detail_segment=row['明细段'],
                product_segment=row['产品段'],
                clause_insurance_segment=row['条款险别段'],
                channel_segment=row['渠道段'],
                vehicle_cash_flow=row['车型现金流'],
                customer_segment=row['客户段'],
                voucher_summary=row['凭证摘要'],
                receipt_number=row['收据号'],
                financial_settlement_number=row['财务结算号'],
                policy_no=row['保单号'],
                endorsement_number=row['批单号'],
                insurance_start_date=row['保险责任起期'],
                insurance_end_date=row['保险责任止期'],
                signing_date=row['签单日期'],
                endorsement_effective_date=row['批单生效日期'],
                settlement_number=row['结算单号'],
                reversal_sequence_number=row['冲正序号'],
                current_period=row['现账期'],
                original_period=row['原账期'],
                scene_id=row['场景ID'],
                batch_number=row['批次号'],
                compressed_number=row['压缩号'],
                contract_group_code=row['合同分组编码']
            )
            vouchers.append(voucher)
        return vouchers


class CostAllocationRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[CostAllocation]:
        df = pd.read_excel(self.file_path, sheet_name="费用分摊")
        result: List[CostAllocation] = []
        for _, row in df.iterrows():
            result.append(CostAllocation(
                policy_no=row['policy_no'],
                year=row['年份'],
                risk_code=row['risk_code'],
                product_segment=row['产品段'],
                signed_premium=row['签单保费'],
                receivable_premium=row['应收保费-不含税'],
                actual_received_premium=row['实收保费-不含税'],
                actual_signed=row['实收-签单'],
                payable_claims=row['应付赔款'],
                actual_claims_paid=row['实付赔款'],
                payable_fees=row['应付手续费'],
                actual_fees_paid=row['实付手续费'],
                allocation_cost_acquisition=row['费用分摊-获取'],
                allocation_cost_claims=row['费用分摊-理赔'],
                allocation_cost_maintenance=row['费用分摊-维持']
            ))
        return result



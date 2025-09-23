import pandas as pd
from 保单处理 import Policy
from 国债收益率 import InterestRateCurve
from 实际现金流 import ActualCashFlow
from 收付凭证 import Voucher
from 精算假设 import ActuarialAssumptions
from 费用分摊 import CostAllocation
from 预期现金流 import ExpectedCashFlow

def read_cost_allocation_from_excel(file_path):
    df = pd.read_excel(file_path,sheet_name="费用分摊")

    cost_allocations = []
    for index, row in df.iterrows():
        cost_allocation = CostAllocation(
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
        )
        cost_allocations.append(cost_allocation)

    return cost_allocations
# 创建保单实例
def load_curves_from_excel(file_path):
    """
    Load interest rate curves from an Excel file.

    Parameters:
    - file_path: Path to the Excel file.

    Returns:
    - A list of InterestRateCurve objects.
    """
    # Read the Excel file
    df = pd.read_excel(file_path)

    # List to store InterestRateCurve objects
    curves = []

    # Iterate through rows in the dataframe
    for _, row in df.iterrows():
        name = row['曲线名称']
        date = row['日期']

        # Extract rates as a dictionary
        rates = {
            "3M": row['3月'], "6M": row['6月'], "1Y": row['1年'],
            "3Y": row['3年'], "5Y": row['5年'], "7Y": row['7年'],
            "10Y": row['10年'], "30Y": row['30年']
        }

        # Create an InterestRateCurve object and add it to the list
        curve = InterestRateCurve(name, date, rates)
        curves.append(curve)

    return curves
def load_policy_info_from_excel(file_path):
    # 读取 Excel 文件
    df = pd.read_excel(file_path, sheet_name="Sheet1",dtype={'class_code': str})

    # 遍历每一行数据，将其存储为 Policy 实例
    policies = []
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

    return policies

def filter_policies(policies):
    # 使用字典来累加同一 policy_no 的 sum_premium_no_tax
    premium_totals = {}

    for policy in policies:
        if policy.policy_no not in premium_totals:
            premium_totals[policy.policy_no] = 0
        premium_totals[policy.policy_no] += policy.sum_premium_no_tax

    # 过滤掉 sum_premium_no_tax 总和为 0 的政策
    filtered_policies = [policy for policy in policies if premium_totals[policy.policy_no] != 0]

    return filtered_policies
def load_assumptions_from_excel(file_path):
    # 读取 Excel 文件，假设表格名称为 "Assumptions"
    df = pd.read_excel(file_path, sheet_name="Assumptions",dtype={'险种大类': str})

    # 遍历每一行数据，将其存储为 ActuarialAssumptions 实例
    assumptions = []
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
def load_receipt_vouchers_from_excel(file_path):
    # 读取 Excel 文件，假设表格名称为 "Receipts"
    df = pd.read_excel(file_path, sheet_name="收付系统")

    # 遍历每一行数据，将其存储为 ReceiptVoucher 实例
    vouchers = []
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


def main():
    policy_info_file_path = '蓄电池BBA保单信息.xlsx'
    assumptions_file_path = '精算假设.xlsx'
    voucher_file_path = '收付凭证1.xlsx'
    cost_allocation_file_path = "费用分摊1.xlsx"
    curves_file_path = "国债利率.xlsx"
    curves = load_curves_from_excel(curves_file_path)
    policies = load_policy_info_from_excel(policy_info_file_path)
    policies = filter_policies(policies)
    vouchers = load_receipt_vouchers_from_excel(voucher_file_path)
    assumptions = load_assumptions_from_excel(assumptions_file_path)
    cost_allocations = read_cost_allocation_from_excel(cost_allocation_file_path)
    LRC_sum = 0
    bel_sum = 0
    csm_sum = 0
    ra_sum = 0
    balance_sum = 0
    csm_start_sum = 0
    yi_fa_sheng_sum = 0
    confirm_data =  {
    "policy_no": [],
    "policy.bel": [],
    "policy.yi_fa_sheng": [],
    "policy.ra": [],
    "policy.csm": [],
    "policy.sum": [],
    "policy.acquisition_balance": [],
    "policy.bel_start": [],
    "policy.ra_start": [],
    "policy.csm_start": []
    }

    voucher_gens = []
    for policy in policies:
        if pd.isna(policy.certi_no) :
            policy.expected_cash_flow = ExpectedCashFlow(
                policy=policy,
                policies=policies,
                assumptions=assumptions,
                curves=curves
            )
            policy.expected_cash_flow.compute_data(policies)

            policy.actual_cash_flow = ActualCashFlow(policy, vouchers, cost_allocations)
            policy.actual_cash_flow.compute_data()

            policy.generate_lrc_units()
            LRC_sum += policy.lrc_2023
            bel_sum += policy.bel_2023
            csm_sum += policy.csm_2023
            ra_sum += policy.ra_2023
            balance_sum += policy.end_balance
            csm_start_sum += policy.csm_start
            yi_fa_sheng_sum += policy.yi_fa_sheng_2023
            voucher_gens.extend(policy.voucher_gens)


            print(f"Processing policy: {policy.policy_no}, balance_sum: {policy.end_balance}")
            confirm_data["policy_no"].append(policy.policy_no)
            confirm_data["policy.bel"].append(policy.bel_2023)
            confirm_data["policy.yi_fa_sheng"].append(policy.yi_fa_sheng_2023)
            confirm_data["policy.ra"].append(policy.ra_2023)
            confirm_data["policy.csm"].append(policy.csm_2023)
            confirm_data["policy.sum"].append(policy.lrc_2023)
            confirm_data["policy.acquisition_balance"].append(policy.acquisition_2023)
            confirm_data["policy.bel_start"].append(policy.bel_start)
            confirm_data["policy.ra_start"].append(policy.ra_start)
            confirm_data["policy.csm_start"].append(policy.csm_start)


            # 创建 DataFrame
    df = pd.DataFrame(confirm_data)

    print("导出凭证",voucher_gens)     # 导出到 Excel 文件
    data = [
        {
            "凭证ID": voucher.voucher_id,
            "保单号": voucher.policy_number,
            "科目代码": voucher.subject_code,
            "科目名称": voucher.subject_name,
            "金额": voucher.amount,
        }
        for voucher in voucher_gens
    ]

    # 创建 DataFrame
    vouchers_data = pd.DataFrame(data)

    # 导出为 Excel 文件
    vouchers_data.to_excel("vouchers.xlsx", index=True)
    #导出全量数据
    output_file = 'policy_data.xlsx'
    df.to_excel(output_file, index=True)

    print(f"Data exported to {output_file} successfully.")
    print("LRC_sum",LRC_sum,"bel_sum",bel_sum,"yi_fa_sheng_sum",yi_fa_sheng_sum,"csm_sum",csm_sum,"ra_sum",ra_sum,"balance_sum",balance_sum,"csm_start_sum",csm_start_sum)
# 只有当此脚本作为主程序运行时，才会执行 main() 函数
if __name__ == "__main__":
    main()
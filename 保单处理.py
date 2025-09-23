import calendar
import pandas as pd
from pandas import to_datetime

from 国债收益率 import InterestRateCurve
from 收付凭证 import Voucher
from 生成会计凭证 import VoucherGen
from 费用分摊 import CostAllocation

pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.max_rows', None)   # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.expand_frame_repr', False)  # 不折叠 DataFrame
from datetime import datetime
pd.set_option('display.width', 1000)
# 假设你已定义了 ActualCashFlow 和 ExpectedCashFlow 类
from 实际现金流 import ActualCashFlow
from 未到期计算单元 import LRCUnit
from 精算假设 import ActuarialAssumptions
from 预期现金流 import ExpectedCashFlow


class Policy:
    def __init__(self, id, bi_id, policy_no, certi_no, class_code, risk_code, com_code,
                 business_nature, channel_type, app_li_type, customer_group, center_code,
                 segment1, segment2, segment6, segment7, segment8, app_li_code, car_kind_code,
                 use_nature_code, business_type, coins_flag, present_flag, card_flag,
                 d_fee_flag, under_write_date, first_plan_end_date, return_flag,
                 max_pay_rate, min_pay_rate, start_date, end_date, valid_date,
                 loss_ratio_init, loss_ratio_agr, modify_type, revise_flag, amount_limit,
                 plan_revise_flag, pay_no, plan_date, sum_premium_no_tax, currency,
                 stat_date, create_time, last_update_time, create_user,warranty,premium_date):
        """ 初始化保单对象 """
        # 将所有参数赋值给实例属性
        self.id = id
        self.bi_id = bi_id
        self.policy_no = policy_no
        self.certi_no = certi_no
        self.class_code = class_code
        self.risk_code = risk_code
        self.com_code = com_code
        self.business_nature = business_nature
        self.channel_type = channel_type
        self.app_li_type = app_li_type
        self.customer_group = customer_group
        self.center_code = center_code
        self.segment1 = segment1
        self.segment2 = segment2
        self.segment6 = segment6
        self.segment7 = segment7
        self.segment8 = segment8
        self.app_li_code = app_li_code
        self.car_kind_code = car_kind_code
        self.use_nature_code = use_nature_code
        self.business_type = business_type
        self.coins_flag = coins_flag
        self.present_flag = present_flag
        self.card_flag = card_flag
        self.d_fee_flag = d_fee_flag
        self.under_write_date = under_write_date
        self.first_plan_end_date = first_plan_end_date
        self.return_flag = return_flag
        self.max_pay_rate = max_pay_rate
        self.min_pay_rate = min_pay_rate
        self.start_date = start_date
        self.end_date = end_date
        self.valid_date = valid_date
        self.loss_ratio_init = loss_ratio_init
        self.loss_ratio_agr = loss_ratio_agr
        self.modify_type = modify_type
        self.revise_flag = revise_flag
        self.amount_limit = amount_limit
        self.plan_revise_flag = plan_revise_flag
        self.pay_no = pay_no
        self.plan_date = plan_date
        self.sum_premium_no_tax = sum_premium_no_tax
        self.currency = currency
        self.stat_date = stat_date
        self.create_time = create_time
        self.last_update_time = last_update_time
        self.create_user = create_user
        self.warranty = int(warranty)
        self.voucher_gens = []
        self.premium_date = premium_date
        if isinstance(start_date, pd.Timestamp):
            # 将 Timestamp 转换为字符串格式
            date_obj = start_date.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(start_date, str):
            # 将斜杠替换为横线
            date_obj = start_date.replace('/', '-')
        else:
            raise ValueError("start_date must be a string or a pandas Timestamp")

        date_obj = datetime.strptime(date_obj, "%Y-%m-%d %H:%M:%S")
        self.warranty_date = date_obj.replace(year = date_obj.year + self.warranty)
        #self.warranty_date = start_date.replace(year = start_date.year + warranty)


        # 将日期字段转换为 datetime 对象
        self.start_date = pd.to_datetime(self.start_date) if self.start_date else None
        self.end_date = pd.to_datetime(self.end_date) if self.end_date else None
        self.premium_date = pd.to_datetime(self.premium_date) if self.premium_date else None
        # 初始化属性
        self.assumption = None  # 初始为 None
        self.expected_cash_flow = None  # 初始为 None
        self.actual_cash_flow = None  # 初始为 None
        self.lrc_units = []
        self.lrc_2023 = 0
        self.bel_2023 = 0
        self.ra_2023 = 0
        self.end_balance = 0
        self.csm_2023 = 0
        self.csm_start = 0
        self.yi_fa_sheng_2023 = 0
        self.acquisition_2023 = 0
        self.bel_start = 0
        self.ra_start = 0
    def display(self):
        """ 显示保单信息 """
        policy_dict = {key: getattr(self, key) for key in vars(self) if not key.startswith('_')}

    def get_assumption(self, assumptions):
        # 过滤符合条件的 assumption
        self.assumption = next((
            assumption for assumption in assumptions
            if assumption.year == self.start_date.year and assumption.class_code == self.class_code
        ), None)

        # 检查是否找到匹配的 assumption
        if not self.assumption:
            print(f"No assumption found for year {self.start_date.year} and class_code {self.class_code}.")
            return None  # 或者可以返回一个空的列表

        return self.assumption

    def get_expected_cash_flow(self,policies,assumptions):
        self.expected_cash_flow = ExpectedCashFlow(self,policies,assumptions)
        self.expected_cash_flow.compute_data(policies)
        return self.expected_cash_flow

    def get_actual_cash_flow(self):
        """ 获取实际现金流 """
        return self.actual_cash_flow

    def generate_lrc_units(self):
        lrc_units = []  # 存储 LRCUnit 实例的列表
        previous_end_balance = [0] * 6  # 初始化前一个期末余额
        new_business = [
            self.expected_cash_flow.data.loc["预期保费流入", "折现值"]  +
            self.expected_cash_flow.data.loc["预期赔付支出", "折现值"] * (-1)+
            self.expected_cash_flow.data.loc["预期间接理赔费用","折现值"]*(-1)+
            self.expected_cash_flow.data.loc["预期获取费用", "折现值"] * (-1)+
            self.expected_cash_flow.data.loc["预期维持费用", "折现值"]* (-1),
            0,
            self.expected_cash_flow.data.loc["非金融风险", "总计"] * (-1),
            0,
            self.expected_cash_flow.data.loc["预期保费流入", "折现值"] * (-1) +
            self.expected_cash_flow.data.loc["预期赔付支出", "折现值"] +
            self.expected_cash_flow.data.loc["预期间接理赔费用", "折现值"] +
            self.expected_cash_flow.data.loc["预期获取费用", "折现值"] +
            self.expected_cash_flow.data.loc["预期维持费用", "折现值"] +
            self.expected_cash_flow.data.loc["非金融风险", "总计"] ,
            0
        ]
        self.bel_start = new_business[0]
        self.ra_start = new_business[2]
        self.csm_start = new_business[4]
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606010101", (-1) * self.expected_cash_flow.data.loc["预期保费流入", "折现值"]))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606030101",
                                            (-1) * new_business[4]))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606010103",
                                            self.expected_cash_flow.data.loc["预期获取费用", "折现值"]))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606010102",
                                            self.expected_cash_flow.data.loc["预期赔付支出", "折现值"] + self.expected_cash_flow.data.loc["预期间接理赔费用","折现值"] + self.expected_cash_flow.data.loc["预期维持费用", "折现值"]))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606020101",
                                            self.expected_cash_flow.data.loc["非金融风险", "总计"]))

        self.voucher_gens.append(VoucherGen(self.policy_no, "2606010801",
                                            self.expected_cash_flow.data.loc["预期保费流入", "总计"]))
        previous_and_new = [prev + new for prev, new in zip(previous_end_balance, new_business)]
        # 获取预期现金流和实际现金流数据

        actual_cash_flow_data = self.actual_cash_flow.data
        assumption_data = self.assumption
        remain_days = self.expected_cash_flow.data.loc["经过时间","总计"]
        # 使用 start_date 和 end_date
        IACF_opening = 0
        voucher_cost_sum = 0
        voucher_ra_interest_sum = 0
        voucher_csm_interest_sum = 0
        voucher_bel_interest_sum = 0
        voucher_acquisition_cost_sum = 0
        voucher_IACF_amortization_sum = 0
        voucher_ra_amortization_sum = 0
        voucher_csm_amortization_sum = 0
        for year in range(self.start_date.year, self.end_date.year + 1):
            # 创建 LRCUnit 实例
            lrc_unit = LRCUnit(year)
            self.expected_cash_flow.update_old_rate()
            premium_interest_sum = 0  # 初始化利息总和
            premium_sum = 0
            expected_premium_sum = 0
            acquisition_cost_interest_sum = 0
            acquisition_cost_sum = 0
            expected_acquisition_cost_sum = 0
            expected_claim_cost_sum = 0
            maintain_cost_sum = 0
            expected_maintain_cost_sum = 0
            claim_cost_interest_sum = 0
            claim_cost_sum = 0
            expected_claim_sum = 0
            claim_cost_suspense_sum = 0 #赔付挂账汇总
            claim_suspense_sum= 0
            claim_sum = 0
            maintain_cost_suspense_sum = 0
            acquisition_cost_suspense_sum = 0
            expected_premium_future_value_sum = 0
            expected_acquisition_cost_future_value_sum = 0
            amortization_sum = 0

            if year == self.end_date.year:

                end_of_year = self.end_date
            else:

                end_of_year = datetime(year, 12, 31, 23, 59, 59)
            for column in self.expected_cash_flow.data:

                try:
                    if column not in ["总计", "折现值"]:
                        column_date = pd.to_datetime(column)
                        if column_date.year >= year and column_date.month == 12 and column_date.day == 31 and column_date.year != self.end_date.year:
                            amortization_sum += self.expected_cash_flow.data.loc["经过时间", column]

                    column_year = pd.to_datetime(column).year
                    if column_year == year:  # 检查提取的年份是否等于当前年份

                        expected_acquisition_cost_sum += self.expected_cash_flow.data.loc["预期获取费用", column]
                        expected_premium_sum += self.expected_cash_flow.data.loc["预期保费流入", column]
                        expected_premium_future_value_sum += self.expected_cash_flow.data.loc["预期保费流入", column]* (1+self.expected_cash_flow.data.loc["当年折现率", column]) **((end_of_year - column).days/365)

                        expected_acquisition_cost_future_value_sum += self.expected_cash_flow.data.loc[
                                                                 "预期获取费用", column] * (1+self.expected_cash_flow.data.loc["当年折现率", column]) ** (
                                                                         (end_of_year - column).days / 365)
                        expected_claim_sum += self.expected_cash_flow.data.loc["预期赔付支出", column]
                        expected_maintain_cost_sum += self.expected_cash_flow.data.loc["预期维持费用", column]
                        expected_claim_cost_sum += self.expected_cash_flow.data.loc["预期间接理赔费用", column]
                except ValueError:
                    continue
            amortization_sum += self.expected_cash_flow.data.loc["经过时间", self.end_date]
            if year != self.end_date.year:
                amortization_ratio = self.expected_cash_flow.data.loc["经过时间", datetime(year,12,31,23,59,59)] /amortization_sum
            elif year == self.end_date.year:
                amortization_ratio = self.expected_cash_flow.data.loc["经过时间", self.end_date] /amortization_sum
            for column in actual_cash_flow_data:

                try:
                    # 将列名转换为日期，提取年份
                    column_date = pd.to_datetime(column)
                    column_year = pd.to_datetime(column).year
                    if column_year == year:  # 检查提取的年份是否等于当前年份
                        days_remaining = (end_of_year - pd.to_datetime(column)).days
                        discount_rate_to_end_of_year = (1 + self.expected_cash_flow.assumption.discount_rate+ self.expected_cash_flow.curve.get_spot_rate((end_of_year - self.start_date).days + 1)) ** (
                                                                   ((end_of_year - self.start_date).days + 1) / 365) / (
                                                                       1 + self.expected_cash_flow.assumption.discount_rate+ self.expected_cash_flow.curve.get_spot_rate((column_date - self.start_date).days + 1)) ** (
                                                                       ((column_date - self.start_date).days + 1) / 365)
                        # 获取折现率
                        #discount_rate = self.expected_cash_flow.data.loc["折现率", end_of_year]  # 确保行和列索引正确
                        # 计算利息



                        #claim_interest = actual_cash_flow_data.loc["实际赔付支出", column] * ((1 + discount_rate) ** (days_remaining / (366 if calendar.isleap(year) else 365)) - 1)
                        #claim_interest_sum += claim_interest
                        claim_cost = actual_cash_flow_data.loc["实际理赔费用", column]
                        claim_cost_sum += claim_cost

                        claim_cost_suspense = actual_cash_flow_data.loc["理赔费用挂账", column]
                        claim_cost_suspense_sum += claim_cost_suspense

                        claim_suspense = actual_cash_flow_data.loc["赔付挂账", column]
                        claim_suspense_sum += claim_suspense

                        claim = actual_cash_flow_data.loc["实际赔付支出", column]
                        claim_sum += claim

                        maintain_cost = actual_cash_flow_data.loc["实际维持费用", column]
                        maintain_cost_sum += maintain_cost

                        maintain_cost_suspense = actual_cash_flow_data.loc["维持费用挂账", column]
                        maintain_cost_suspense_sum += maintain_cost_suspense

                        premium = actual_cash_flow_data.loc["实际保费流入", column]
                        premium_sum += premium
                        #print("days_remaining",days_remaining,actual_cash_flow_data.loc["实际保费流入", column])
                        premium_interest = actual_cash_flow_data.loc["实际保费流入", column] * ((1 + self.expected_cash_flow.data.loc["当年折现率", end_of_year]) ** (
                                    days_remaining / 365) - 1)
                        premium_interest_sum += premium_interest  # 累加利息总和

                        acquisition_cost = actual_cash_flow_data.loc["实际获取费用", column]
                        acquisition_cost_sum += acquisition_cost
                        acquisition_cost_suspense = actual_cash_flow_data.loc["获取费用挂账", column]
                        acquisition_cost_suspense_sum += acquisition_cost_suspense
                        acquisition_cost_interest = actual_cash_flow_data.loc["实际获取费用", column] * ((1 + self.expected_cash_flow.data.loc["当年折现率", end_of_year]) ** (days_remaining / 365) - 1)
                        acquisition_cost_interest_sum += acquisition_cost_interest

                except ValueError:
                    continue
            #计算获取费用

            date_columns = [col for col in self.expected_cash_flow.data.columns if isinstance(col, str) and '/' in col]
            date_columns = pd.to_datetime(date_columns, errors='coerce')  # 使用错误处理，无法解析的将为 NaT


            # 进行年份筛选
            year_filtered_columns = date_columns[date_columns.year == year]

            #经验调整
            #保费收入

            premium_diff = (-1)*expected_premium_future_value_sum -  (-1)*(premium_interest_sum + premium_sum)

            #获取费用

            acquisition_cost_diff = expected_acquisition_cost_future_value_sum - (acquisition_cost_sum + acquisition_cost_interest_sum)
            #acquisition_cost_diff = expected_acquisition_cost_future_value_sum - (acquisition_cost_sum )
            #赔付支出

            claim_diff = expected_claim_sum - claim_suspense_sum
            #理赔费用
            claim_cost_diff = expected_claim_cost_sum - claim_cost_suspense_sum

            #维持费用

            maintenance_cost_diff = expected_maintain_cost_sum - maintain_cost_suspense_sum

            discount_rate_to_end_of_year = (1 + self.expected_cash_flow.assumption.discount_rate + self.expected_cash_flow.curve.get_spot_rate(
                                                   (end_of_year - self.start_date).days + 1)) ** (
                                                   ((end_of_year - self.start_date).days + 1) / 365) / (
                                                   1 + self.expected_cash_flow.assumption.discount_rate + self.expected_cash_flow.curve.get_spot_rate(
                                               (column_date - self.start_date).days + 1)) ** (
                                                   ((column_date - self.start_date).days + 1) / 365)

            # 计算利息
            interest = previous_end_balance[0] *  ((1+self.expected_cash_flow.data.loc["当年折现率", end_of_year])**(self.expected_cash_flow.data.loc["经过时间",end_of_year]/365)-1)+ new_business[0] * ((1+self.expected_cash_flow.data.loc["当年折现率", end_of_year])**(((end_of_year - self.start_date).days+1)/365)-1)
            csm_interest = previous_end_balance[4] * ((1+self.expected_cash_flow.data.loc["初始当年折现率", end_of_year])**(self.expected_cash_flow.data.loc["经过时间",end_of_year]/365)-1)+ new_business[4] * ((1+self.expected_cash_flow.data.loc["初始当年折现率", end_of_year])**(((end_of_year - self.start_date).days+1)/365)-1)
            """
            RA_interest = previous_end_balance[2] * ((1 + self.expected_cash_flow.assumption.discount_rate) ** (
                        self.expected_cash_flow.data.loc["经过时间", end_of_year] / 365) - 1) + new_business[2] * (
                                       (1 + self.expected_cash_flow.assumption.discount_rate) ** (
                                           ((end_of_year - self.start_date).days + 1) / 365) - 1)
            """
            if year in [2017,2018,2019,2020,2021,2022,2023]:
                pre_total_discounted_value_for_non_financial,pre_total_discounted_value,pre_total_ra_discounted_value,pre_total_acquisition_discounted_value = self.expected_cash_flow.compute_discounted_data(datetime(year + 1, 1, 1))
                self.expected_cash_flow.get_assumption(self.expected_cash_flow.assumptions, year + 1)
                self.expected_cash_flow.get_interest_curve(datetime(year,12,31))
                self.expected_cash_flow.compute_data(self.expected_cash_flow.policies)

                after_total_discounted_value_for_non_financial,after_total_discounted_value,after_total_ra_discounted_value,after_total_acquisition_discounted_value = self.expected_cash_flow.compute_discounted_data(datetime(year + 1, 1, 1))
            else:
                pre_total_discounted_value_for_non_financial, pre_total_discounted_value, pre_total_ra_discounted_value, pre_total_acquisition_discounted_value = 0,0,0,0
                after_total_discounted_value_for_non_financial, after_total_discounted_value, after_total_ra_discounted_value, after_total_acquisition_discounted_value=0,0,0,0
            assumption_bel_diff_for_non_financial = (-1)*after_total_discounted_value_for_non_financial - (-1)*pre_total_discounted_value_for_non_financial
            assumption_ra_diff = (-1) * after_total_ra_discounted_value - (-1) * pre_total_ra_discounted_value
            assumption_total_diff = assumption_bel_diff_for_non_financial+assumption_ra_diff
            #RA、CSM摊销考虑保修期
            warranty_period = (end_of_year  - self.warranty_date).days +1


            if warranty_period >= 0:
                if self.warranty_date.year == year:

                    csm_amortization = (-1) * ((-1) * premium_diff + (-1) * acquisition_cost_diff + previous_end_balance[4] + new_business[
                        4] + csm_interest + (-1)*assumption_total_diff) * ((
                     (end_of_year - self.warranty_date).days + 1)/ ((self.end_date - self.warranty_date).days +1))

                    ra_amortization = (-1) * (previous_end_balance[2] + new_business[2]) * ((
                     (end_of_year - self.warranty_date).days + 1)/ ((self.end_date - self.warranty_date).days +1))
                else:
                    print("year", year)
                    print("self.end_date",self.end_date )
                    print("self.warranty_date",self.warranty_date)
                    print("(self.end_date - self.warranty_date).days + 1",(self.end_date - self.warranty_date).days + 1)
                    ra_amortization = (-1) * (previous_end_balance[2] + new_business[2]) * amortization_ratio

                    csm_amortization = (-1) * ((-1) * premium_diff + (-1) * acquisition_cost_diff + previous_end_balance[4] + new_business[4] + csm_interest + (-1)*assumption_total_diff) * amortization_ratio
            else:
                ra_amortization = 0
                csm_amortization = 0

            if year == self.start_date.year:

                new_business_IACF = self.expected_cash_flow.data.loc["预期获取费用", "折现值"] * (1+self.expected_cash_flow.data.loc["调整前当年折现率", end_of_year]) ** ((
                        (datetime(year, 12, 31) - self.start_date).days + 1)/365)
                IACF_amortization = (new_business_IACF * (1+self.expected_cash_flow.data.loc["调整前当年折现率", end_of_year]) ** (
                                                 ((end_of_year - self.start_date).days + 1) / 365) + (
                                         -1) * expected_acquisition_cost_future_value_sum + acquisition_cost_suspense_sum + acquisition_cost_interest_sum + after_total_acquisition_discounted_value - pre_total_acquisition_discounted_value) * amortization_ratio
            elif year == self.end_date.year:
                new_business_IACF = 0

                IACF_amortization = (IACF_opening * (1+self.expected_cash_flow.data.loc["调整前当年折现率", end_of_year]) ** (((datetime(year, 12, 31) - datetime(year, 1,
                                                                                                  1)).days + 1) / 365) + new_business_IACF * (1+self.expected_cash_flow.data.loc["调整前当年折现率", end_of_year]) ** (
                                                 ((end_of_year - self.start_date).days + 1) / 365) + (
                                         -1) * expected_acquisition_cost_future_value_sum + acquisition_cost_suspense_sum + acquisition_cost_interest_sum + after_total_acquisition_discounted_value - pre_total_acquisition_discounted_value) * amortization_ratio

            else:
                new_business_IACF = 0

                IACF_amortization = (IACF_opening*(1+self.expected_cash_flow.data.loc["调整前当年折现率", end_of_year])**(((datetime(year,12,31) - datetime(year,1,1)).days + 1)/365) + new_business_IACF *(1+self.expected_cash_flow.data.loc["调整前当年折现率", end_of_year])**(((end_of_year - self.start_date).days + 1)/365)+(-1)*expected_acquisition_cost_future_value_sum + acquisition_cost_suspense_sum +acquisition_cost_interest_sum + after_total_acquisition_discounted_value - pre_total_acquisition_discounted_value)*amortization_ratio
            print("IACF_opening  before", IACF_opening)

            IACF_opening = (IACF_opening*(1+self.expected_cash_flow.data.loc["当年折现率", end_of_year])**(((datetime(year,12,31) - datetime(year,1,1)).days + 1)/365) + new_business_IACF *(1+self.expected_cash_flow.data.loc["当年折现率", end_of_year])**(((end_of_year - self.start_date).days + 1)/365)+(-1)*expected_acquisition_cost_future_value_sum + acquisition_cost_suspense_sum +acquisition_cost_interest_sum + after_total_acquisition_discounted_value - pre_total_acquisition_discounted_value) - IACF_amortization
            lrc_unit.IACF_amortization = IACF_amortization
            print("IACF_opening  after", IACF_opening)
            values = {
                "履约现金流未到期": [
                    previous_end_balance[0],  #期初
                    new_business[0],
                    premium_sum * (-1),
                    acquisition_cost_sum,
                    (-1) * premium_interest_sum + acquisition_cost_interest_sum + interest,
                    claim_suspense_sum,
                    claim_cost_suspense_sum,
                    maintain_cost_suspense_sum,#维持费用挂账
                    0,0, 0,0,
                    premium_diff,#经验调整-保费收入
                    claim_diff,
                    claim_cost_diff,
                    maintenance_cost_diff,
                    acquisition_cost_diff,
                    (-1)*after_total_discounted_value_for_non_financial - (-1)*pre_total_discounted_value_for_non_financial,
                    (-1)*(after_total_discounted_value - after_total_discounted_value_for_non_financial) - (-1)*(pre_total_discounted_value - pre_total_discounted_value_for_non_financial),
                    0, 0, 0, 0
                ],
                "履约现金流已发生": [
                    previous_end_balance[1],
                    new_business[1],
                    0,  # "收取保费-初始"
                    0,  # 保单获取成本
                    0,  # 利息
                    (-1) * claim_suspense_sum,  # 赔付挂账
                    (-1) * claim_cost_suspense_sum,  # 理赔费用挂账
                    (-1) * maintain_cost_suspense_sum,  # 维持费用挂账
                    0,#支付保单获取成本
                    claim_sum,  # 支付赔款
                    claim_cost_sum,  # 支付理赔费用
                    maintain_cost_sum,  # 支付维持费用
                    0,  # 经验调整
                    0,  # 经验调整
                    0,  # 经验调整
                    0,  # 经验调整
                    0,  # 经验调整
                    0, 0, 0, 0, 0, 0
                ],
                "非金融风险未到期": [
                    previous_end_balance[2],
                    new_business[2],
                    0,0,
                    0,#非金融风险不计息
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,
                    (-1)*after_total_ra_discounted_value -(-1)* pre_total_ra_discounted_value,
                    0,0,
                    #(-1)*(previous_end_balance[2]+new_business[2])*(expected_cash_flow_data.loc["经过时间",end_of_year]/remain_days),
                    ra_amortization,
                    0, 0
                ],
                "非金融风险已发生": [
                    previous_end_balance[3],
                    new_business[3],
                    0,
                    0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0,
                    0, 0, 0, 0,0
                ],
                "合同服务边际": [
                    previous_end_balance[4],
                    new_business[4],
                    0, 0,
                    csm_interest,
                    0, 0, 0,0,0,
                    0,0,
                    (-1) *premium_diff,
                    0, 0, 0,
                    (-1) * acquisition_cost_diff,
                    after_total_discounted_value_for_non_financial - pre_total_discounted_value_for_non_financial + after_total_ra_discounted_value -pre_total_ra_discounted_value,
                    0,0,0,
                    #((-1)*((-1) *premium_diff+(-1) * acquisition_cost_diff +previous_end_balance[4]+new_business[4]+previous_and_new[4] * ((1+self.expected_cash_flow.assumption.discount_rate)**(expected_cash_flow_data.loc["经过时间",end_of_year]/365)-1))*(expected_cash_flow_data.loc["经过时间",end_of_year]/remain_days)),
                    csm_amortization,
                    0
                ],
                "合计": [
                    previous_end_balance[5],
                    0,
                    0,
                    0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0
                ]
            }
            for key in values:
                values[key][-1] = sum(values[key][:-1])

            num_rows = len(next(iter(values.values())))


            # 遍历每一行
            for i in range(num_rows):
                row_sum = 0  # 初始化行和
                for key in values:
                    if key != '合计':  # 跳过“合计”列
                        row_sum += values[key][i]  # 累加每一列的值
                values['合计'][i] = row_sum  # 将行和赋值给“合计”列


            # 计算合计行
            values["合计"][-1] = sum(values[key][-1] for key in values if key != "合计")  # 其他行的总和

            lrc_unit.populate_data(values)
            lrc_units.append(lrc_unit)  # 添加 LRCUnit 到列表
            new_business = [0]*6
            previous_end_balance = [values[key][-1] for key in values]
            previous_and_new = [prev + new for prev, new in zip(previous_end_balance, new_business)]

            if year == self.end_date.year:
                end_of_year = self.end_date
            else:
                end_of_year = datetime(year, 12, 31, 23, 59, 59)
            remain_days = remain_days - self.expected_cash_flow.data.loc["经过时间",end_of_year]
            if year <= 2023:
                """
                self.vouchers.append(VoucherGen(self.policy_no, self.start_date.year, "2606011001",
                                                (-1) * lrc_unit.data.loc["保单获取成本","履约现金流未到期"]))
                self.vouchers.append(VoucherGen(self.policy_no, year, "2606010601",
                                                (-1)*(lrc_unit.data.loc["赔付挂账","履约现金流未到期"] +lrc_unit.data.loc["理赔费用挂账","履约现金流未到期"] +lrc_unit.data.loc["维持费用挂账","履约现金流未到期"] +lrc_unit.data.loc["经验调整-赔付支出","履约现金流未到期"] +lrc_unit.data.loc["经验调整-理赔费用","履约现金流未到期"] +lrc_unit.data.loc["经验调整-维持费用","履约现金流未到期"])))
                self.vouchers.append(VoucherGen(self.policy_no, year, "2606030401",(-1)*lrc_unit.data.loc["CSM摊销","合同服务边际"]))
                self.vouchers.append(VoucherGen(self.policy_no, year, "2606011601",
                                                (-1)*lrc_unit.IACF_amortization))
                self.vouchers.append(VoucherGen(self.policy_no, year, "2606011701",
                                                lrc_unit.IACF_amortization))
                self.vouchers.append(VoucherGen(self.policy_no, year, "2606020301",
                                                (-1)*lrc_unit.data.loc["RA摊销","非金融风险未到期"]))
                self.vouchers.append(VoucherGen(self.policy_no, year, "2606011403",
                                                (-1)*lrc_unit.data.loc["利息", "履约现金流未到期"]))
                self.vouchers.append(VoucherGen(self.policy_no, year, "2606020601",
                                                (-1)*lrc_unit.data.loc["利息", "非金融风险未到期"]))
                self.vouchers.append(VoucherGen(self.policy_no, year, "2606030301",
                                                (-1)*lrc_unit.data.loc["利息", "合同服务边际"]))
                """
                voucher_acquisition_cost_sum +=  (-1) * lrc_unit.data.loc["保单获取成本","履约现金流未到期"]
                voucher_cost_sum += (-1)*(lrc_unit.data.loc["赔付挂账","履约现金流未到期"] +lrc_unit.data.loc["理赔费用挂账","履约现金流未到期"] +lrc_unit.data.loc["维持费用挂账","履约现金流未到期"] +lrc_unit.data.loc["经验调整-赔付支出","履约现金流未到期"] +lrc_unit.data.loc["经验调整-理赔费用","履约现金流未到期"] +lrc_unit.data.loc["经验调整-维持费用","履约现金流未到期"])
                voucher_csm_amortization_sum += (-1)*lrc_unit.data.loc["CSM摊销","合同服务边际"]
                voucher_IACF_amortization_sum += (-1)*lrc_unit.IACF_amortization
                voucher_ra_amortization_sum += (-1)*lrc_unit.data.loc["RA摊销","非金融风险未到期"]
                voucher_bel_interest_sum += (-1)*lrc_unit.data.loc["利息", "履约现金流未到期"]
                voucher_ra_interest_sum += (-1)*lrc_unit.data.loc["利息", "非金融风险未到期"]
                voucher_csm_interest_sum += (-1)*lrc_unit.data.loc["利息", "合同服务边际"]
            #导出
            #lrc_unit.data.to_excel(f"计量单元{year}.xlsx", index=True)
            if year == 2023:  # 使用双等号进行条件判断

                self.lrc_2023 = values["合计"][-1]
                self.bel_2023 = values["履约现金流未到期"][-1]
                self.csm_2023 = values["合同服务边际"][-1]
                self.ra_2023 = values["非金融风险未到期"][-1]
                self.yi_fa_sheng_2023 = values["履约现金流已发生"][-1]
                self.acquisition_2023 = IACF_opening

                # 获取“合计”列的最后一个值并赋给 lrc_2023
                if pd.isna(self.lrc_2023):

                    import pdb;
                    pdb.set_trace()


            lrc_unit.display()

            #file_name= f"Unit_{year}.xlsx"
            #lrc_unit.data.to_excel(file_name, index=True)
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606011001",
                                            voucher_acquisition_cost_sum))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606010601",
                                            voucher_cost_sum))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606030401", voucher_csm_amortization_sum))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606011601",
                                            (-1) * voucher_IACF_amortization_sum))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606011701",
                                            voucher_IACF_amortization_sum))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606020301",
                                            voucher_ra_amortization_sum))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606011403",
                                            voucher_bel_interest_sum))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606020601",
                                            voucher_ra_interest_sum))
        self.voucher_gens.append(VoucherGen(self.policy_no, "2606030301",
                                            voucher_csm_interest_sum))
        """
        vouchers_data = [voucher.to_dict() for voucher in self.vouchers]
        # 创建 DataFrame
        voucher_gen = pd.DataFrame(vouchers_data)

        # 导出至 Excel
        voucher_gen.to_excel('会计凭证生成.xlsx', index=True)
        """
        self.end_balance = lrc_units[-1].data.loc["期末余额","履约现金流未到期"]
        self.csm_start = lrc_units[0].data.loc["新业务","合同服务边际"]

        # 保存到实例，便于外部导出每年度 104 表
        self.lrc_units = lrc_units
        return lrc_units


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

def get_policy_instance(policy_instance_policy_no,policies):
    for policy in policies:

        if str(policy.policy_no) == policy_instance_policy_no and pd.isna(policy.certi_no):
            return policy


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


# Example usage





# 设置精算假设

# 将以下演示代码放入入口保护，避免被 import 时执行
if __name__ == "__main__":
    # 初始化预期现金流对象（示例单保单跑数）
    policy_instance_policy_no = str("1440000000004501220170000002")
    policy_info_file_path = '蓄电池BBA保单信息.xlsx'
    assumptions_file_path = '精算假设.xlsx'
    voucher_file_path = '收付凭证1.xlsx'
    cost_allocation_file_path = "费用分摊.xlsx"
    curves_file_path = "国债利率.xlsx"  # Replace with your Excel file path
    policies = load_policy_info_from_excel(policy_info_file_path)
    policies = filter_policies(policies)
    policy_instance = get_policy_instance(policy_instance_policy_no,policies)
    if policy_instance:
        print("找到的Policy实例:", policy_instance,"start_date:", policy_instance.start_date)
    else:
        print("没有找到匹配的Policy实例")
    vouchers = load_receipt_vouchers_from_excel(voucher_file_path)
    cost_allocations = read_cost_allocation_from_excel(cost_allocation_file_path)
    policy_instance.expected_cash_flow = ExpectedCashFlow(
        policy = policy_instance,
        policies= policies   ,  # 正确引用属性并已转换为 datetime
        assumptions=load_assumptions_from_excel(assumptions_file_path),
        curves = load_curves_from_excel(curves_file_path)
    )
    print("在这里进入预期现金流计算")
    policy_instance.expected_cash_flow.compute_data(policies)
    print("计算完毕")
    print("在这里进入实际现金流计算")
    policy_instance.actual_cash_flow = ActualCashFlow(policy_instance,vouchers,cost_allocations)

    policy_instance.actual_cash_flow.compute_data()
    print("-----------实际现金流")
    policy_instance.actual_cash_flow.display()
    #policy_instance.actual_cash_flow.data.to_excel("实际现金流.xlsx",index = True)
    print("-------调整前预期现金流")
    policy_instance.expected_cash_flow.display()
    #policy_instance.expected_cash流.data.to_excel("预期现金流.xlsx",index = True)

    #policy_instance.actual_cash_flow.populate_data(data_values)

    policy_instance.generate_lrc_units()
    print("调整后的预期现金流")
    policy_instance.expected_cash_flow.display()
    #policy_instance.expected_cash_flow.data.to_excel("调整后预期现金流.xlsx",index = True)

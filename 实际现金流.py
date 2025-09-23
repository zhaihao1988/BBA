import pandas as pd
from datetime import datetime


pd.set_option('display.float_format', lambda x: '%.2f' % x)
class ActualCashFlow:
    def __init__(self, policy, vouchers,cost_allocations):
        self.policy_no = policy.policy_no
        self.start_date = policy.start_date
        self.end_date = policy.end_date
        self.vouchers = vouchers
        self.cost_allocations = cost_allocations
        # 生成年份列表
        self.years = list(range(self.start_date.year, self.end_date.year + 1))

        # 创建 DataFrame，增加挂账项
        self.data = pd.DataFrame(0,index=[
            "剩余时间",
            "实际保费流入",
            "实际赔付支出",
            "赔付挂账",
            "实际获取费用",
            "获取费用挂账",
            "实际理赔费用",
            "理赔费用挂账",
            "实际维持费用",
            "维持费用挂账",
            "实际非金融风险调整"
        ], columns=[],dtype=float)

    def compute_data(self):
        initial_year_expenses = {
            "1440000000004501220170000001": 0,
            "1440000000004501220170000002": 401374.08,
            "1440003000004501220190000001": 0,
            "1440003000004501220190000002": 434209.92,
            "1440003000004501220190000003": 74715.00,
            "1440003000004501220190000004": 42303.53,
            "1440003000004501220190000005": 47460.60,
            "1440003000004501220190000006": 130560.00,
            "1440003000004501220190000007": 45644.15,
            "1440003000004501220190000008": 5528.66,
            "1440003000004501220190000009": 40881.28,
            "1440003000004501220190000010": 10245.35
        }
        for voucher in self.vouchers:
            if voucher.policy_no == self.policy_no:
                voucher_date_str = voucher.voucher_date.replace('/', '-').split(' ')[0]
                voucher_date = datetime.strptime(voucher_date_str, "%Y-%m-%d")
                voucher_date_str = voucher_date.strftime('%Y-%m-%d')
                #voucher_date = datetime.strptime(voucher.voucher_date.replace('/', '-'), "%Y-%m-%d")
                #voucher_date_str = voucher_date.strftime('%Y-%m-%d')
                #voucher_date_str = voucher_date_str.split(' ')[0]
                if voucher_date_str not in self.data.columns:
                    self.data[voucher_date_str] = float(0)
                year = voucher_date.year
                # 确保年份在数据框的列中

                if year == self.end_date.year:
                    end_of_year = self.end_date
                else:
                    end_of_year = datetime(year, 12, 31)
                self.data.loc["剩余时间",voucher_date_str] = (end_of_year - voucher_date).days
                    #print("voucher.accounting_subject",voucher.accounting_subject,"voucher.accounting_type",voucher.accounting_type)
                    # 检查会计科目是否为6031000000
                """
                if voucher.accounting_subject in ["1122020000", "1124010000", "2203020000", "2206010000"] and voucher.accounting_type == "RP":
                    if voucher.accounting_subject == "1124010000":
                        value = float(voucher.debit_credit) / 1.06
                    else:
                        value = float(voucher.debit_credit)  # 确保值为float

                    self.data.loc["实际保费流入", voucher_date_str] += float(-value)
                        # 检查会计科目为2206030000、2204010000或2206030000，累加理赔费用挂账
                """
                if voucher.accounting_subject  ==  "6031000000" and voucher.accounting_type == "AC":
                    self.data.loc["实际保费流入", voucher_date_str] += float(-voucher.debit_credit)

                if voucher.accounting_subject in ["2206030000", "2204010000","2204030000"] and voucher.accounting_type == "RP":
                    self.data.loc["实际赔付支出", voucher_date_str] += float(voucher.debit_credit)

                    # 检查会计科目为6511010000或6511020101，累加赔付挂账
                if voucher.accounting_subject in ["6511010000", "6511020101"] and voucher.accounting_type == "AC":
                     self.data.loc["赔付挂账", voucher_date_str] += float(voucher.debit_credit)

                if voucher.accounting_subject == "6421010000" and voucher.accounting_type == "AC":

                    self.data.loc["实际获取费用",voucher_date_str] += float(voucher.debit_credit)
                    self.data.loc["获取费用挂账", voucher_date_str] += float(voucher.debit_credit)
                if voucher.policy_no in initial_year_expenses:
                    policy_year = int(voucher.policy_no[-11:-7])  # 提取年份部分
                    initial_expense = initial_year_expenses.get(voucher.policy_no, 0)

                        # 确保提取的年份在数据框中
                    if policy_year in self.years:
                        self.data[datetime(policy_year, 12, 31).strftime('%Y-%m-%d')] = float(0)
                        #print("datetime(policy_year, 12, 31)",datetime(policy_year, 12, 31).strftime('%Y-%m-%d'))
                        self.data.loc["实际获取费用", datetime(policy_year, 12, 31).date().strftime('%Y-%m-%d')] = initial_expense
        for cost_allocation in self.cost_allocations:
            if cost_allocation.policy_no == self.policy_no:
                year = int(cost_allocation.year)
                year_end = datetime(year, 12, 31).date().strftime('%Y-%m-%d')

                if year_end not in self.data.columns:
                    self.data[year_end] = float(0)
                self.data.loc["实际获取费用", year_end] += cost_allocation.allocation_cost_acquisition
                self.data.loc["获取费用挂账", year_end] += cost_allocation.allocation_cost_acquisition
                self.data.loc["实际理赔费用", year_end] += cost_allocation.allocation_cost_claims
                self.data.loc["理赔费用挂账", year_end] += cost_allocation.allocation_cost_claims
                self.data.loc["实际维持费用", year_end] += cost_allocation.allocation_cost_maintenance
                self.data.loc["维持费用挂账", year_end] += cost_allocation.allocation_cost_maintenance
       # print("问题保单号：",self.policy_no)
        self.data.columns = pd.to_datetime(self.data.columns)
        self.data = self.data.reindex(sorted(self.data.columns), axis=1)
    def display(self):
        """显示 DataFrame"""
        print(f"保单号: {self.policy_no}")
        print(f"保单起始日期: {self.start_date.date()}")
        print(f"保单终止日期: {self.end_date.date()}")
        print(self.data)



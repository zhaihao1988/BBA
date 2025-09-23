import numpy as np
import pandas as pd
import calendar
from 国债收益率 import InterestRateCurve
from datetime import datetime
pd.set_option('display.float_format', lambda x: '%.2f' % x)
from 未到期计算单元 import LRCUnit
from 精算假设 import ActuarialAssumptions
from bba.services.expected_components import (
    calculate_expected_claims,
    calculate_claim_expense,
    calculate_maintenance_cost,
    calculate_non_financial_risk,
)
from bba.services.discount import compute_discounted_data

class ExpectedCashFlow:
    def __init__(self, policy,policies,assumptions,curves):
        self.policy = policy
        self.policy_no = policy.policy_no
        self.class_code = policy.class_code
        self.start_date = policy.start_date
        self.end_date = policy.end_date
        self.policies = policies
        self.assumptions = assumptions
        # 本地缓存需在首次查找前初始化
        self._assumption_cache = {}
        self._curve_cache = {}
        self.assumption = self.get_assumption(assumptions,policy.start_date.year)
        self.curves = curves
        self.curve = self.get_interest_curve(policy.start_date)
        # 创建行名
        self.index = [
            "经过时间", "剩余时间","折现率","初始折现率","调整前折现率", "当年折现率","调整前当年折现率","初始当年折现率","折现因子","调整前折现因子", "预期保费流入", "预期保费流入折现值",
            "预期赔付支出", "预期获取费用","预期获取费用折现值",
            "预期间接理赔费用", "预期维持费用", "非金融风险"
        ]

        self.data = pd.DataFrame(0,index=self.index,columns=[])
    def update_old_rate(self):
        for column in self.data:
            if column not in ["总计","折现值"]:
                self.data.loc["调整前折现率",column] = self.data.loc["折现率",column]
                self.data.loc["调整前折现因子", column] = self.data.loc["折现因子", column]
                self.data.loc["调整前当年折现率", column] = self.data.loc["当年折现率", column]

    def get_interest_curve(self, date):
        # 如果 date 是字符串，先转换为 datetime.date
        if isinstance(date, str):
            from datetime import datetime
            date = datetime.strptime(date, "%Y-%m-%d").date()

        # 缓存命中
        key = (date.year, date.month, date.day)
        cached = self._curve_cache.get(key)
        if cached is not None:
            return cached

        # 打印调试信息
        print(f"Looking for curve on date: {date}")
        print(f"Available dates: {[curve.date for curve in self.curves]}")

        # 查找符合条件的 curve
        self.curve = next((
            curve for curve in self.curves
            if curve.date.year == date.year and curve.date.month == date.month and curve.date.day == date.day
        ), None)

        # 如果找不到完全匹配的日期，尝试找最近的早于 date 的日期
        if not self.curve:
            print(f"No exact curve found for {date}. Searching for the nearest earlier date.")
            sorted_curves = sorted(self.curves, key=lambda c: c.date)  # 确保按日期排序
            self.curve = next(
                (curve for curve in reversed(sorted_curves) if curve.date < date),
                None
            )

        # 最终结果
        if not self.curve:
            print(f"No curve found earlier than {date}.")
            return None  # 或者可以返回一个空值

        print(f"Curve found for date {self.curve.date}.")
        # 写入缓存
        if self.curve is not None:
            self._curve_cache[key] = self.curve
        return self.curve
    def get_assumption(self, assumptions,year):
        # 标准化 risk_code 为6位，补齐前导零
        standardized_risk_code = str(self.policy.risk_code).zfill(6)
        cache_key = (year, standardized_risk_code)
        cached = self._assumption_cache.get(cache_key)
        if cached is not None:
            return cached
        
        # 添加日志：打印 year 和 standardized_risk_code
        print(f"DEBUG: Searching assumption for year={year}, class_code={standardized_risk_code}")
        
        # 添加日志：打印所有 assumptions 的 year 和 class_code
        print("DEBUG: Available assumptions:")
        for ass in assumptions:
            print(f"  - year={ass.year}, class_code={ass.class_code}")
        
        # 先尝试精确匹配
        self.assumption = next((
            assumption for assumption in assumptions
            if assumption.year == year and assumption.class_code == standardized_risk_code
        ), None)

        # 若无精确匹配，回退到同险种下最近且不晚于目标年的年份
        if not self.assumption:
            candidates = [a for a in assumptions if a.class_code == standardized_risk_code and a.year <= year]
            if candidates:
                self.assumption = max(candidates, key=lambda a: a.year)
                print(f"DEBUG: Fallback to nearest earlier assumption: year={self.assumption.year}, class_code={self.assumption.class_code}")

        # 若仍无，回退到该险种下的最新年份
        if not self.assumption:
            candidates_any = [a for a in assumptions if a.class_code == standardized_risk_code]
            if candidates_any:
                self.assumption = max(candidates_any, key=lambda a: a.year)
                print(f"DEBUG: Fallback to latest available assumption: year={self.assumption.year}, class_code={self.assumption.class_code}")

        # 最终检查
        if not self.assumption:
            print(f"DEBUG: No assumption found for year {year} and class_code {standardized_risk_code} after fallbacks.")
            return None

        # 写入缓存
        self._assumption_cache[cache_key] = self.assumption
        return self.assumption

    def compute_discounted_data(self, date):
        return compute_discounted_data(
            data=self.data,
            policy_start_date=self.policy.start_date,
            assumption_discount_rate=self.assumption.discount_rate,
            date=date,
        )

    def compute_data(self,policies):
        # 健壮性：确保已有 assumption，否则自动回退获取
        if self.assumption is None:
            print("DEBUG: self.assumption is None at compute_data start. Trying to fetch with fallback logic.")
            self.assumption = self.get_assumption(self.assumptions, self.start_date.year)
            if self.assumption is None:
                raise ValueError("Assumption not found even after fallbacks. Please check 精算假设.xlsx 数据是否包含对应险种与年份。")
        self.data.loc["预期保费流入"] = 0
        self.data.loc["预期保费流入折现值"] = 0
        self.data.loc["预期获取费用"] = 0
        self.data.loc["预期获取费用折现值"] = 0

        for year in range(self.start_date.year, self.end_date.year + 1):
            start_of_year = datetime(year, 1, 1, 0, 0, 0)
            if year == self.start_date.year:

                end_of_year = datetime(year, 12, 31, 23, 59, 59)
                elapsed_days = (end_of_year - self.start_date).days + 1
            elif year == self.end_date.year:
                elapsed_days = (self.end_date - datetime(year, 1, 1, 0, 0, 0)).days + 1
                end_of_year = self.end_date
            else:
                # 检查该年是否为闰年
                elapsed_days = 366 if calendar.isleap(year) else 365
                end_of_year = datetime(year, 12, 31, 23, 59, 59)
            #cumulative_elapsed_days += elapsed_days  # 更新累计经过时间
            for row in self.data.index:
                if row in ["初始折现率","调整前折现率", "调整前当年折现率","初始当年折现率","调整前折现因子"]:  # 跳过特定行
                    continue
                else:
                    self.data.loc[row, end_of_year] = float(0)

            self.data.loc["经过时间", end_of_year] = elapsed_days
            self.data.loc["剩余时间", end_of_year] = self.data.loc["经过时间", end_of_year] - elapsed_days
            self.data.loc["折现率", end_of_year] = self.assumption.discount_rate + self.curve.get_spot_rate((end_of_year - self.policy.start_date).days + 1)
            self.data.loc["当年折现率",end_of_year] = ((1 + self.assumption.discount_rate + self.curve.get_spot_rate((end_of_year - self.start_date).days + 1))**(((end_of_year - self.start_date).days + 1)/365)/(1+ self.assumption.discount_rate + self.curve.get_spot_rate((max(self.start_date,start_of_year) - self.start_date).days))**((max(self.start_date,start_of_year) - self.start_date).days/365))**(1/(((end_of_year - max(self.start_date,start_of_year)).days+1)/365)) -1
            cumulative_days = (end_of_year - self.start_date).days + 1
            self.data.loc["折现因子", end_of_year] = 1/((1+self.data.loc["折现率", end_of_year])**(cumulative_days/365))
            if np.isnan(self.data.loc["初始折现率",end_of_year]):
                self.data.loc["初始折现率", end_of_year] = self.data.loc["折现率", end_of_year]
                self.data.loc["初始当年折现率",end_of_year] = self.data.loc["当年折现率",end_of_year]

            # 计算折现值
            discounted_values = []

            for policy in policies:

                if policy.premium_date.year == year and policy.policy_no == self.policy_no:
                    if pd.isna(policy.sum_premium_no_tax):
                        premium_income = 0
                    else:
                        premium_income = policy.sum_premium_no_tax
                    premium_income_date = policy.premium_date
                    # 计算折现天数
                    days_difference = (premium_income_date - self.start_date).days + 1

                    # 计算折现值
                    discounted_value = premium_income / ((1 + self.assumption.discount_rate) ** (days_difference / 365))
                    discounted_values.append(discounted_value)
                    start_of_year = premium_income_date.replace(month=1, day=1)
                    if premium_income_date not in self.data.columns:
                        self.data[premium_income_date] = float(0)
                    self.data.loc["预期保费流入", premium_income_date] += float(premium_income)
                    self.data.loc["预期获取费用", premium_income_date] += float(premium_income) * self.assumption.expected_acquisition_cost_rate
                    self.data.loc["经过时间", premium_income_date] = self.data.loc["经过时间", end_of_year]
                    self.data.loc["剩余时间", premium_income_date] = (end_of_year - premium_income_date).days
                    #self.data.loc["折现率", premium_income_date] = 1+ self.assumption.discount_rate + self.curve.get_spot_rate(end_of_year - (max(self.start_date,premium_income_date.replace(premium_income_date.year - 1, 12,31,23,59,59)) - self.policy.start_date).days +1)
                    year_interest_rate = ((1 + self.assumption.discount_rate + self.curve.get_spot_rate((end_of_year - self.start_date).days + 1))**(((end_of_year - self.start_date).days + 1)/365)/(1+ self.assumption.discount_rate + self.curve.get_spot_rate((max(self.start_date,start_of_year) - self.start_date).days))**((max(self.start_date,start_of_year) - self.start_date).days/365))**(1/(((end_of_year - max(self.start_date,start_of_year)).days+1)/365)) -1
                    #year_interest_rate = self.curve.get_spot_rate((end_of_year - max(self.start_date,start_of_year)).days + 1)
                    self.data.loc["折现率", premium_income_date] = ((1+self.assumption.discount_rate + self.curve.get_spot_rate((max(self.start_date,start_of_year) - self.start_date).days))**((max(self.start_date,start_of_year) - self.start_date).days/365) * (1+year_interest_rate)**(((premium_income_date - max(self.start_date,start_of_year)).days +1)/365))** (1/(((premium_income_date - self.start_date).days + 1)/365))-1
                    self.data.loc["折现因子",premium_income_date] = 1/((1+self.data.loc["折现率", premium_income_date])**(days_difference/365))
                    self.data.loc["当年折现率", premium_income_date] = year_interest_rate
                    self.data.loc["预期保费流入折现值", premium_income_date] += premium_income * self.data.loc["折现因子",premium_income_date]
                    self.data.loc["预期获取费用折现值", premium_income_date] += self.data.loc["预期保费流入折现值", premium_income_date] * self.assumption.expected_acquisition_cost_rate
                    if self.data.loc["初始折现率", premium_income_date] ==0:
                        self.data.loc["初始折现率", premium_income_date] = self.data.loc["折现率", premium_income_date]
                        self.data.loc["初始当年折现率", premium_income_date] = self.data.loc["当年折现率", premium_income_date]
        self.data["总计"] = None
        self.data["折现值"] = None  # 初始化折现值列为None
        self.data.loc["预期保费流入", "总计"] = self.data.loc["预期保费流入"] .sum()
        self.data.loc["预期保费流入", "折现值"] = self.data.loc["预期保费流入折现值"].sum()
        self.data.loc["经过时间", "总计"] = (self.end_date - self.start_date).days + 1
        for year in range(self.start_date.year, self.end_date.year + 1):
            if year == self.end_date.year:
                end_of_year = self.end_date
            else:
                end_of_year = datetime(year, 12, 31, 23, 59, 59)
            self.data.loc["预期赔付支出", end_of_year] = calculate_expected_claims(self.policy, self.assumption, self.data, end_of_year)
            self.data.loc["预期间接理赔费用", end_of_year] = calculate_claim_expense(self.policy, self.assumption, self.data, end_of_year)
            self.data.loc["预期维持费用", end_of_year] = calculate_maintenance_cost(self.policy, self.assumption, self.data, end_of_year)
            #self.data.loc["预期获取费用折现值", year] = self.calculate_expected_acquisition_cost_discounted(year)


        self.data.loc["预期赔付支出", "总计"] = self.data.loc["预期赔付支出"].sum()

        self.data.loc["预期获取费用", "总计"] = self.data.loc["预期获取费用"].sum()

        self.data.loc["预期间接理赔费用", "总计"] = self.data.loc["预期间接理赔费用"].sum()

        self.data.loc["预期维持费用", "总计"] = self.data.loc["预期维持费用"].sum()
        self.data.loc["预期维持费用", "折现值"] = (self.data.loc["预期维持费用"] * self.data.loc["折现因子"]).sum()
        self.data.loc["预期保费流入折现值", "总计"] = self.data.loc["预期保费流入折现值"].sum()

        self.data.loc["预期获取费用折现值", "总计"] = self.data.loc["预期获取费用折现值"].sum()


        self.data.loc["预期赔付支出", "折现值"] = (self.data.loc["预期赔付支出"] * self.data.loc["折现因子"]).sum()
        self.data.loc["预期获取费用", "折现值"] = self.data.loc["预期获取费用折现值","总计"]
        self.data.loc["预期间接理赔费用", "折现值"] = (
                    self.data.loc["预期间接理赔费用"] * self.data.loc["折现因子"]).sum()
        self.data.loc["预期保费流入折现值", "折现值"] = self.data.loc["预期保费流入折现值", "总计"]
        self.data.loc["预期获取费用折现值", "折现值"] = self.data.loc["预期获取费用折现值", "总计"]
        for year in range(self.start_date.year, self.end_date.year + 1):

            if year == self.end_date.year:

                end_of_year = self.end_date
            else:

                end_of_year = datetime(year, 12, 31, 23, 59, 59)
            self.data.loc["非金融风险", end_of_year] = calculate_non_financial_risk(self.policy, self.assumption, self.data, end_of_year)
            self.data.loc["非金融风险折现值", end_of_year] = self.data.loc["非金融风险", end_of_year] * self.data.loc["折现因子", end_of_year]
        total_non_financial_risk = self.data.loc["非金融风险"].sum(min_count=1)
        self.data.loc["非金融风险", "总计"] = total_non_financial_risk if not np.isnan(total_non_financial_risk) else 0
        total_non_financial_risk_discounted = self.data.loc["非金融风险折现值"].sum(min_count=1)
        self.data.loc["非金融风险折现值", "总计"] = total_non_financial_risk_discounted if not np.isnan(total_non_financial_risk_discounted) else 0
        self.data.loc["非金融风险", "折现值"] = self.data.loc["非金融风险折现值", "总计"]


        # 过滤掉“总计”和“折现值”列
        columns_to_sort = [col for col in self.data.columns if col not in ["总计", "折现值"]]

        # 对剩余列进行排序
        sorted_columns = sorted(columns_to_sort)

        # 创建新的列顺序，确保“总计”和“折现值”在最后
        new_order = sorted_columns + ["总计", "折现值"]

        # 重新索引 DataFrame
        self.data = self.data.loc[:, new_order]


    def calculate_claim_expense(self, end_of_year):
        return calculate_claim_expense(self.policy, self.assumption, self.data, end_of_year)

    #def calculate_maintenance_cost(self, end_of_year):
    #    maintenance_cost_rate = self.assumption.maintenance_cost_rate
    #    return (self.data.loc["预期保费流入", "总计"] * maintenance_cost_rate * self.data.loc["经过时间", end_of_year]) / \
    #        self.data.loc["经过时间", "总计"]

    def calculate_maintenance_cost(self, end_of_year):
        return calculate_maintenance_cost(self.policy, self.assumption, self.data, end_of_year)


    def calculate_non_financial_risk(self, end_of_year):
        return calculate_non_financial_risk(self.policy, self.assumption, self.data, end_of_year)

        """
        non_financial_risk_adjustment = self.assumption.non_financial_risk_adjustment
        return ((self.data.loc["预期赔付支出", "总计"] + self.data.loc["预期间接理赔费用", "总计"] + self.data.loc["预期维持费用", "总计"]) * non_financial_risk_adjustment * self.data.loc[
            "经过时间", end_of_year]) / self.data.loc["经过时间", "总计"]
        """
    #def calculate_expected_claims(self, end_of_year):
    #    return (self.data.loc["预期保费流入","总计"] * self.assumption.claims_rate * self.data.loc["经过时间",end_of_year]) / self.data.loc["经过时间","总计"]

    def calculate_expected_claims(self, end_of_year):
        return calculate_expected_claims(self.policy, self.assumption, self.data, end_of_year)

    def calculate_discount_factor(self, cumulative_days):
        discount_rate = self.assumption.discount_rate
        return 1 / (1 + discount_rate) ** (cumulative_days / 365)

    def calculate_expected_acquisition_cost_discounted(self, end_of_year):
        acquisition_cost_rate = self.assumption.expected_acquisition_cost_rate
        return self.data.loc["预期保费流入折现值", end_of_year] * acquisition_cost_rate

    def display(self):
        pd.set_option('display.max_rows', None)  # 显示所有行
        pd.set_option('display.max_columns', None)  # 显示所有列
        pd.set_option('display.width', None)  # 不限制宽度
        pd.set_option('display.float_format', '{:.6f}'.format)  # 设置浮点数格式
        print(self.data)


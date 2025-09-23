import pandas as pd
from datetime import datetime
pd.set_option('display.float_format', lambda x: '%.6f' % x)
class ActuarialAssumptions:
    def __init__(self, year,class_code,discount_rate, expected_acquisition_cost_rate, claims_rate,
                 claim_expense_rate, maintenance_cost_rate, non_financial_risk_adjustment):
        self.year = year
        self.class_code = class_code
        self.discount_rate = discount_rate
        self.expected_acquisition_cost_rate = expected_acquisition_cost_rate
        self.claims_rate = claims_rate
        self.claim_expense_rate = claim_expense_rate
        self.maintenance_cost_rate = maintenance_cost_rate
        self.non_financial_risk_adjustment = non_financial_risk_adjustment

    def display(self):
        print(f"年份: {self.year}")
        print(f"折现率: {self.discount_rate}")
        print(f"预期获取费用率: {self.expected_acquisition_cost_rate}")
        print(f"赔付率: {self.claims_rate}")
        print(f"理赔费用率: {self.claim_expense_rate}")
        print(f"维持费用率: {self.maintenance_cost_rate}")
        print(f"非金融风险调整比例: {self.non_financial_risk_adjustment}")
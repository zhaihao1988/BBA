import pandas as pd
pd.set_option('display.float_format', lambda x: '%.6f' % x)
class LRCUnit:
    def __init__(self, year):
        # 创建列名
        self.columns = [
            "履约现金流未到期",
            "履约现金流已发生",
            "非金融风险未到期",
            "非金融风险已发生",
            "合同服务边际",
            "合计"
        ]

        # 创建行名
        self.index = [
            "期初余额",
            "新业务",
            "收取保费-初始",
            "保单获取成本",
            "利息",
            "赔付挂账",
            "理赔费用挂账",
            "维持费用挂账",
            "支付保单获取成本",
            "支付赔款",
            "支付理赔费用",
            "支付维持费用",
            "经验调整-保费收入",
            "经验调整-赔付支出",
            "经验调整-理赔费用",
            "经验调整-维持费用",
            "经验调整-获取费用",
            "假设变化-非经济假设",
            "假设变化-经济假设",
            "获取费用摊销",
            "RA摊销",
            "CSM摊销",
            "期末余额"
        ]

        # 创建空的 DataFrame
        self.data = pd.DataFrame(index=self.index, columns=self.columns)
        self.year = year  # 存储单一年度
        self.IACF_amortization = 0

    def populate_data(self, values):
        """接受字典形式的值填充 DataFrame"""
        for key, row in values.items():
            if key in self.data.columns:  # 确保列名有效
                self.data[key] = row

    def display(self):
        # 显示年度
        print("年度:", self.year)
        print("获取费用摊销：", self.IACF_amortization)
        # 显示 DataFrame
        print(self.data)


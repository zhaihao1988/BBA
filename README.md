# BBA 跑批重构入口

## 依赖安装

```bash
pip install -r requirements.txt
```

## 运行

- 单保单：
```bash
python main_bba.py single --policy-no 1440000000004501220170000002 \
  --policies 蓄电池BBA保单信息.xlsx \
  --assumptions 精算假设.xlsx \
  --curves 国债利率.xlsx \
  --vouchers 收付凭证1.xlsx \
  --costs 费用分摊.xlsx
```
- 全量：
```bash
python main_bba.py batch \
  --policies 蓄电池BBA保单信息.xlsx \
  --assumptions 精算假设.xlsx \
  --curves 国债利率.xlsx \
  --vouchers 收付凭证1.xlsx \
  --costs 费用分摊.xlsx
```

## 输出

- out/single_policy_<policy_no>_<timestamp>.xlsx 核心汇总
- out/vouchers_<policy_no>_<timestamp>.xlsx 凭证明细
- out/expected_cash_flow_<policy_no>_<timestamp>.xlsx 预期现金流明细
- out/actual_cash_flow_<policy_no>_<timestamp>.xlsx 实际现金流明细

## 配置

- 会计科目映射：`bba/config/chart_of_accounts.yml`

import argparse
from bba.app.usecases import run_single_policy, run_full_batch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BBA 跑批入口：支持单保单与全量")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # 单保单
    p_single = sub.add_parser("single", help="按保单号跑一张单")
    p_single.add_argument("--policy-no", required=True, help="保单号")
    p_single.add_argument("--policies", default="蓄电池BBA保单信息.xlsx")
    p_single.add_argument("--assumptions", default="精算假设.xlsx")
    p_single.add_argument("--curves", default="国债利率.xlsx")
    p_single.add_argument("--vouchers", default="收付凭证1.xlsx")
    p_single.add_argument("--costs", default="费用分摊.xlsx")

    # 全量
    p_batch = sub.add_parser("batch", help="全量跑批")
    p_batch.add_argument("--policies", default="蓄电池BBA保单信息.xlsx")
    p_batch.add_argument("--assumptions", default="精算假设.xlsx")
    p_batch.add_argument("--curves", default="国债利率.xlsx")
    p_batch.add_argument("--vouchers", default="收付凭证1.xlsx")
    p_batch.add_argument("--costs", default="费用分摊.xlsx")
    p_batch.add_argument("--workers", type=int, default=1, help="并行进程数，默认1为串行")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "single":
        result = run_single_policy(
            policy_no=args.policy_no,
            policy_path=args.policies,
            assumptions_path=args.assumptions,
            curves_path=args.curves,
            vouchers_path=args.vouchers,
            cost_allocation_path=args.costs,
        )
        print("单保单完成：", result)
    elif args.cmd == "batch":
        result = run_full_batch(
            policy_path=args.policies,
            assumptions_path=args.assumptions,
            curves_path=args.curves,
            vouchers_path=args.vouchers,
            cost_allocation_path=args.costs,
            workers=args.workers,
        )
        print("全量完成：", result)


if __name__ == "__main__":
    main()



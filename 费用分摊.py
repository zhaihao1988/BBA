class CostAllocation:
    def __init__(self,
                 policy_no,
                 year,
                 risk_code,
                 product_segment,
                 signed_premium,
                 receivable_premium,
                 actual_received_premium,
                 actual_signed,
                 payable_claims,
                 actual_claims_paid,
                 payable_fees,
                 actual_fees_paid,
                 allocation_cost_acquisition,
                 allocation_cost_claims,
                 allocation_cost_maintenance):
        self.policy_no = policy_no
        self.year = year
        self.risk_code = risk_code
        self.product_segment = product_segment
        self.signed_premium = signed_premium
        self.receivable_premium = receivable_premium
        self.actual_received_premium = actual_received_premium
        self.actual_signed = actual_signed
        self.payable_claims = payable_claims
        self.actual_claims_paid = actual_claims_paid
        self.payable_fees = payable_fees
        self.actual_fees_paid = actual_fees_paid
        self.allocation_cost_acquisition = allocation_cost_acquisition
        self.allocation_cost_claims = allocation_cost_claims
        self.allocation_cost_maintenance = allocation_cost_maintenance

    def __repr__(self):
        return (f"<CostAllocation(policy_no={self.policy_no}, year={self.year}, "
                f"risk_code={self.risk_code}, product_segment={self.product_segment})>")


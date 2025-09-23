class Voucher:
    def __init__(self,
                 voucher_number,
                 voucher_sequence,
                 debit_credit_direction,
                 accounting_subject,
                 accounting_name,
                 voucher_date,
                 original_currency_amount,
                 local_currency_amount,
                 debit_credit,
                 local_currency_code,
                 exchange_rate,
                 accounting_type,
                 business_type,
                 issuing_institution,
                 accounting_institution,
                 company_segment,
                 cost_center,
                 detail_segment,
                 product_segment,
                 clause_insurance_segment,
                 channel_segment,
                 vehicle_cash_flow,
                 customer_segment,
                 voucher_summary,
                 receipt_number,
                 financial_settlement_number,
                 policy_no,
                 endorsement_number,
                 insurance_start_date,
                 insurance_end_date,
                 signing_date,
                 endorsement_effective_date,
                 settlement_number,
                 reversal_sequence_number,
                 current_period,
                 original_period,
                 scene_id,
                 batch_number,
                 compressed_number,
                 contract_group_code):
        self.voucher_number = voucher_number
        self.voucher_sequence = voucher_sequence
        self.debit_credit_direction = debit_credit_direction
        self.accounting_subject = str(accounting_subject).split('.')[0]
        self.accounting_name = accounting_name
        self.voucher_date = voucher_date
        self.original_currency_amount = original_currency_amount
        self.local_currency_amount = local_currency_amount
        self.debit_credit = debit_credit
        self.local_currency_code = local_currency_code
        self.exchange_rate = exchange_rate
        self.accounting_type = accounting_type
        self.business_type = business_type
        self.issuing_institution = issuing_institution
        self.accounting_institution = accounting_institution
        self.company_segment = company_segment
        self.cost_center = cost_center
        self.detail_segment = detail_segment
        self.product_segment = product_segment
        self.clause_insurance_segment = clause_insurance_segment
        self.channel_segment = channel_segment
        self.vehicle_cash_flow = vehicle_cash_flow
        self.customer_segment = customer_segment
        self.voucher_summary = voucher_summary
        self.receipt_number = receipt_number
        self.financial_settlement_number = financial_settlement_number
        self.policy_no = policy_no
        self.endorsement_number = endorsement_number
        self.insurance_start_date = insurance_start_date
        self.insurance_end_date = insurance_end_date
        self.signing_date = signing_date
        self.endorsement_effective_date = endorsement_effective_date
        self.settlement_number = settlement_number
        self.reversal_sequence_number = reversal_sequence_number
        self.current_period = current_period
        self.original_period = original_period
        self.scene_id = scene_id
        self.batch_number = batch_number
        self.compressed_number = compressed_number
        self.contract_group_code = contract_group_code

    def __repr__(self):
        return f"<ReceiptVoucher(voucher_number={self.voucher_number}, voucher_date={self.voucher_date}, policy_number={self.policy_number})>"

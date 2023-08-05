INSERT INTO calaccess_processed_form460schedulefitem (
    filing_id,
    line_item,
    payee_code,
    payee_committee_id,
    payee_title,
    payee_lastname,
    payee_firstname,
    payee_name_suffix,
    payee_city,
    payee_state,
    payee_zip,
    treasurer_title,
    treasurer_lastname,
    treasurer_firstname,
    treasurer_name_suffix,
    treasurer_city,
    treasurer_state,
    payment_code,
    payment_description,
    begin_balance,
    amount_paid,
    amount_incurred,
    end_balance,
    transaction_id,
    parent_transaction_id,
    memo_reference_number,
    memo_code
)
SELECT 
    filing.filing_id,
    item_version.line_item,
    item_version.payee_code,
    item_version.payee_committee_id,
    item_version.payee_title,
    item_version.payee_lastname,
    item_version.payee_firstname,
    item_version.payee_name_suffix,
    item_version.payee_city,
    item_version.payee_state,
    item_version.payee_zip,
    item_version.treasurer_title,
    item_version.treasurer_lastname,
    item_version.treasurer_firstname,
    item_version.treasurer_name_suffix,
    item_version.treasurer_city,
    item_version.treasurer_state,
    item_version.payment_code,
    item_version.payment_description,
    item_version.begin_balance,
    item_version.amount_paid,
    item_version.amount_incurred,
    item_version.end_balance,
    item_version.transaction_id,
    item_version.parent_transaction_id,
    item_version.memo_reference_number,
    item_version.memo_code
FROM calaccess_processed_form460filing filing
JOIN calaccess_processed_form460filingversion filing_version
ON filing.filing_id = filing_version.filing_id
AND filing.amendment_count = filing_version.amend_id
JOIN calaccess_processed_form460schedulefitemversion item_version
ON filing_version.id = item_version.filing_version_id;
INSERT INTO calaccess_processed_form460scheduleaitem (
    filing_id,
    line_item,
    date_received,
    date_received_thru,
    transaction_type,
    transaction_id,
    memo_reference_number,
    contributor_code,
    contributor_committee_id,
    contributor_title,
    contributor_lastname,
    contributor_firstname,
    contributor_name_suffix,
    contributor_city,
    contributor_state,
    contributor_zip,
    contributor_employer,
    contributor_occupation,
    contributor_is_self_employed,
    intermediary_committee_id,
    intermediary_title,
    intermediary_lastname,
    intermediary_firstname,
    intermediary_name_suffix,
    intermediary_city,
    intermediary_state,
    intermediary_zip,
    intermediary_employer,
    intermediary_occupation,
    intermediary_is_self_employed,
    amount,
    cumulative_ytd_amount,
    cumulative_election_amount
)
SELECT 
    filing.filing_id,
    item_version.line_item,
    item_version.date_received,
    item_version.date_received_thru,
    item_version.transaction_type,
    item_version.transaction_id,
    item_version.memo_reference_number,
    item_version.contributor_code,
    item_version.contributor_committee_id,
    item_version.contributor_title,
    item_version.contributor_lastname,
    item_version.contributor_firstname,
    item_version.contributor_name_suffix,
    item_version.contributor_city,
    item_version.contributor_state,
    item_version.contributor_zip,
    item_version.contributor_employer,
    item_version.contributor_occupation,
    item_version.contributor_is_self_employed,
    item_version.intermediary_committee_id,
    item_version.intermediary_title,
    item_version.intermediary_lastname,
    item_version.intermediary_firstname,
    item_version.intermediary_name_suffix,
    item_version.intermediary_city,
    item_version.intermediary_state,
    item_version.intermediary_zip,
    item_version.intermediary_employer,
    item_version.intermediary_occupation,
    item_version.intermediary_is_self_employed,
    item_version.amount,
    item_version.cumulative_ytd_amount,
    item_version.cumulative_election_amount
FROM calaccess_processed_form460filing filing
JOIN calaccess_processed_form460filingversion filing_version
ON filing.filing_id = filing_version.filing_id
AND filing.amendment_count = filing_version.amend_id
JOIN calaccess_processed_form460scheduleaitemversion item_version
ON filing_version.id = item_version.filing_version_id;
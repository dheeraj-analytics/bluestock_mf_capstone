-- 1. Top 5 funds by AUM
SELECT fund_house, MAX(aum_lakh_crore) as latest_aum
FROM fact_aum
GROUP BY fund_house
ORDER BY latest_aum DESC LIMIT 5;

-- 2. Average NAV per month (Using dim_date)
SELECT d.year, d.month, AVG(n.nav) as avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.calendar_date
GROUP BY d.year, d.month;

-- 3. SIP YoY Growth (Assuming fact_sip exists, or derived from transactions)
SELECT strftime('%Y', transaction_date) as yr, SUM(amount_inr) as total_sip
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY yr;

-- 4. Transactions by State (Requires joining dim_investor if separated, or querying direct)
-- Note: Based on provided CSV schemas, state is in the transaction file
SELECT state, COUNT(*) as txn_count, SUM(amount_inr) as total_volume
FROM fact_transactions
GROUP BY state
ORDER BY total_volume DESC;

-- 5. Funds with expense_ratio < 1%
SELECT f.scheme_name, p.expense_ratio_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio_pct < 1.0;

-- 6. Highest single Lumpsum investment
SELECT * FROM fact_transactions WHERE transaction_type = 'Lumpsum' ORDER BY amount_inr DESC LIMIT 1;

-- 7. Fund with highest 3-year return
SELECT f.scheme_name, p.return_3yr_pct 
FROM fact_performance p JOIN dim_fund f ON p.amfi_code = f.amfi_code 
ORDER BY return_3yr_pct DESC LIMIT 1;

-- 8. Transaction volume by KYC Status
SELECT kyc_status, SUM(amount_inr) FROM fact_transactions GROUP BY kyc_status;

-- 9. Volatility check: Max vs Min NAV per scheme
SELECT amfi_code, MAX(nav) as high, MIN(nav) as low, (MAX(nav)-MIN(nav)) as spread
FROM fact_nav GROUP BY amfi_code;

-- 10. Weekend NAV checks 
SELECT COUNT(*) as weekend_records 
FROM fact_nav n 
JOIN dim_date d ON n.date = d.calendar_date 
WHERE d.is_weekend = 1;
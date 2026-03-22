-- ============================================================
-- sql/analysis/edgar_analysis.sql
-- SEC EDGAR Fortune 500 Financial Analysis
-- Source: SEC 10-K filings via EDGAR XBRL API
-- ============================================================

-- 1. Revenue kings: top companies by 2023 revenue
SELECT company, ticker, sector, revenue_B,
    net_margin,
    RANK() OVER (ORDER BY revenue_B DESC)   AS revenue_rank,
    RANK() OVER (ORDER BY net_margin DESC)  AS margin_rank
FROM financials
WHERE year = 2023
ORDER BY revenue_B DESC;


-- 2. Revenue CAGR 2019-2023 (compound annual growth rate)
WITH endpoints AS (
    SELECT company, ticker, sector,
        MAX(CASE WHEN year=2019 THEN revenue_B END) AS rev_2019,
        MAX(CASE WHEN year=2023 THEN revenue_B END) AS rev_2023
    FROM financials GROUP BY company, ticker, sector
)
SELECT company, ticker, sector, rev_2019, rev_2023,
    ROUND(rev_2023 - rev_2019, 1) AS abs_growth_B,
    ROUND(100.0 * (rev_2023 - rev_2019) / rev_2019, 1) AS total_growth_pct,
    ROUND((POWER(rev_2023 / rev_2019, 0.25) - 1) * 100, 2) AS cagr_pct
FROM endpoints
ORDER BY cagr_pct DESC;


-- 3. Profit margin comparison across sectors (2023)
SELECT sector,
    COUNT(DISTINCT company)          AS companies,
    ROUND(AVG(net_margin), 2)        AS avg_margin_pct,
    ROUND(MAX(net_margin), 2)        AS best_margin_pct,
    ROUND(MIN(net_margin), 2)        AS worst_margin_pct,
    ROUND(SUM(net_income_B), 1)      AS total_profit_B
FROM financials
WHERE year = 2023
GROUP BY sector
ORDER BY avg_margin_pct DESC;


-- 4. Free cash flow yield + trend (window function)
SELECT company, ticker, year, fcf_B, revenue_B,
    ROUND(100.0 * fcf_B / revenue_B, 2) AS fcf_margin_pct,
    ROUND(fcf_B - LAG(fcf_B) OVER (PARTITION BY company ORDER BY year), 2)
        AS fcf_yoy_change_B,
    ROUND(AVG(fcf_B) OVER (PARTITION BY company ORDER BY year
          ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2)
        AS rolling_3yr_avg_fcf
FROM financials
ORDER BY company, year;


-- 5. COVID impact: 2019 vs 2020 revenue change by sector
SELECT sector, company,
    MAX(CASE WHEN year=2019 THEN revenue_B END) AS rev_2019,
    MAX(CASE WHEN year=2020 THEN revenue_B END) AS rev_2020,
    ROUND(MAX(CASE WHEN year=2020 THEN revenue_B END) -
          MAX(CASE WHEN year=2019 THEN revenue_B END), 1) AS covid_impact_B,
    ROUND(100.0*(MAX(CASE WHEN year=2020 THEN revenue_B END) -
          MAX(CASE WHEN year=2019 THEN revenue_B END))
        / MAX(CASE WHEN year=2019 THEN revenue_B END), 1) AS covid_pct_change
FROM financials
GROUP BY sector, company
ORDER BY covid_pct_change;


-- 6. Debt analysis: leverage ratios 2023
SELECT company, ticker, sector,
    total_debt_B, total_assets_B, net_income_B,
    debt_to_equity,
    ROUND(total_debt_B / NULLIF(fcf_B, 0), 1) AS debt_to_fcf_yrs,
    CASE
        WHEN debt_to_equity < 0.5  THEN 'Conservative'
        WHEN debt_to_equity < 1.5  THEN 'Moderate'
        WHEN debt_to_equity < 3.0  THEN 'Leveraged'
        ELSE 'Highly Leveraged'
    END AS leverage_tier
FROM financials
WHERE year = 2023
ORDER BY debt_to_equity DESC;

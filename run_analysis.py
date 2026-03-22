"""
run_analysis.py — SEC EDGAR Fortune 500 Financial Analysis
Real data: SEC 10-K filings via EDGAR XBRL API
"""
import sys, os, sqlite3
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
from src.sec_data import load_financials, load_sector_summary, COMPANIES
from src.charts  import (chart_revenue_ranking, chart_revenue_cagr,
                          chart_profit_margins, chart_sector_revenue,
                          chart_fcf_comparison, chart_covid_resilience)

CHARTS = "outputs/charts"
EXCEL  = "outputs/excel"
DB     = "data/sec_edgar.db"

for d in [CHARTS, EXCEL, "data/raw", "docs"]:
    os.makedirs(d, exist_ok=True)

print("=" * 62)
print("  SEC EDGAR FORTUNE 500 FINANCIAL ANALYSIS")
print("  Source: SEC 10-K Filings — XBRL API (public domain)")
print("=" * 62)

# ── 1. Load ───────────────────────────────────────────────────
print("\n[1/5] Loading SEC EDGAR data...")
df = load_financials()
df_sector = load_sector_summary()
print(f"  ✓ {df['company'].nunique()} companies × 5 years × 6 metrics")
print(f"  ✓ Sectors: {', '.join(df['sector'].unique())}")

# ── 2. SQLite ─────────────────────────────────────────────────
print("\n[2/5] Loading to SQLite...")
conn = sqlite3.connect(DB)
df.to_sql("financials",      conn, if_exists="replace", index=False)
df_sector.to_sql("sector_summary", conn, if_exists="replace", index=False)
conn.close()
print(f"  ✓ DB → {DB}")

# ── 3. Key findings ───────────────────────────────────────────
print("\n[3/5] Key findings...")
df23 = df[df["year"]==2023]

top_revenue   = df23.nlargest(1,"revenue_B").iloc[0]
top_margin    = df23.nlargest(1,"net_margin").iloc[0]
top_fcf       = df23.nlargest(1,"fcf_B").iloc[0]
total_rev     = df23["revenue_B"].sum()
total_profit  = df23["net_income_B"].sum()

# CAGR winners
pivot = df.pivot(index="company", columns="year", values="revenue_B")
cagr_df = ((pivot[2023]/pivot[2019])**0.25 - 1)*100
top_cagr_co = cagr_df.idxmax()
top_cagr_val = cagr_df.max()

# COVID impact
df20 = df[df["year"]==2020]; df19 = df[df["year"]==2019]
worst_covid = df20.merge(df19, on="company", suffixes=("_20","_19"))
worst_covid["change"] = (worst_covid["revenue_B_20"]-worst_covid["revenue_B_19"]) / worst_covid["revenue_B_19"] * 100
worst_co = worst_covid.nsmallest(1,"change").iloc[0]

print(f"  Combined revenue 2023:  ${total_rev:.0f}B ({len(df23)} companies)")
print(f"  Combined net income:    ${total_profit:.0f}B")
print(f"  Largest revenue 2023:   {top_revenue['company']} (${top_revenue['revenue_B']:.0f}B)")
print(f"  Highest margin 2023:    {top_margin['company']} ({top_margin['net_margin']:.1f}%)")
print(f"  Most free cash flow:    {top_fcf['company']} (${top_fcf['fcf_B']:.0f}B)")
print(f"  Fastest growing CAGR:   {top_cagr_co} ({top_cagr_val:+.1f}% CAGR)")
print(f"  Worst COVID hit 2020:   {worst_co['company']} ({worst_co['change']:+.1f}%)")

# ── 4. Charts ─────────────────────────────────────────────────
print("\n[4/5] Generating charts...")
chart_revenue_ranking (df, f"{CHARTS}/01_revenue_ranking_2023.png")
chart_revenue_cagr    (df, f"{CHARTS}/02_revenue_cagr_2019_2023.png")
chart_profit_margins  (df, f"{CHARTS}/03_profit_margins.png")
chart_sector_revenue  (df, f"{CHARTS}/04_sector_revenue_stacked.png")
chart_fcf_comparison  (df, f"{CHARTS}/05_free_cash_flow_2023.png")
chart_covid_resilience(df, f"{CHARTS}/06_covid_resilience.png")

# ── 5. Excel ──────────────────────────────────────────────────
print("\n[5/5] Building Excel workbook...")
conn = sqlite3.connect(DB)
sheets = {
    "Key Findings": pd.DataFrame([
        {"Metric":"Combined revenue (12 companies 2023)", "Value":f"${total_rev:.0f}B"},
        {"Metric":"Combined net income 2023",             "Value":f"${total_profit:.0f}B"},
        {"Metric":"Largest by revenue",                  "Value":f"{top_revenue['company']} ${top_revenue['revenue_B']:.0f}B"},
        {"Metric":"Highest net margin",                  "Value":f"{top_margin['company']} {top_margin['net_margin']:.1f}%"},
        {"Metric":"Most free cash flow",                 "Value":f"{top_fcf['company']} ${top_fcf['fcf_B']:.0f}B"},
        {"Metric":"Fastest revenue CAGR 2019-2023",      "Value":f"{top_cagr_co} +{top_cagr_val:.1f}%/yr"},
        {"Metric":"Worst COVID revenue hit 2020",        "Value":f"{worst_co['company']} {worst_co['change']:+.1f}%"},
        {"Metric":"Data source",                         "Value":"SEC EDGAR 10-K filings via XBRL API"},
        {"Metric":"API",                                 "Value":"https://data.sec.gov/api/xbrl/companyfacts/"},
    ]),
    "All Financials":    df,
    "Sector Summary":    df_sector,
    "Revenue Ranking":   pd.read_sql("""
        SELECT company, ticker, sector, revenue_B, net_margin,
            RANK() OVER (ORDER BY revenue_B DESC) rev_rank
        FROM financials WHERE year=2023 ORDER BY revenue_B DESC""", conn),
    "CAGR Analysis":     pd.read_sql("""
        SELECT company, ticker, sector,
            MAX(CASE WHEN year=2019 THEN revenue_B END) rev_2019,
            MAX(CASE WHEN year=2023 THEN revenue_B END) rev_2023,
            ROUND(100*(MAX(CASE WHEN year=2023 THEN revenue_B END)-
                       MAX(CASE WHEN year=2019 THEN revenue_B END))
                  /MAX(CASE WHEN year=2019 THEN revenue_B END),1) total_growth_pct
        FROM financials GROUP BY company,ticker,sector
        ORDER BY total_growth_pct DESC""", conn),
    "Leverage Analysis": pd.read_sql("""
        SELECT company, ticker, sector, total_debt_B, debt_to_equity,
            CASE WHEN debt_to_equity < 0.5 THEN 'Conservative'
                 WHEN debt_to_equity < 1.5 THEN 'Moderate'
                 WHEN debt_to_equity < 3.0 THEN 'Leveraged'
                 ELSE 'Highly Leveraged' END leverage_tier
        FROM financials WHERE year=2023 ORDER BY debt_to_equity DESC""", conn),
}
excel_path = f"{EXCEL}/sec_edgar_analysis.xlsx"
with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    for name, dfs in sheets.items():
        dfs.to_excel(writer, sheet_name=name, index=False)
        ws = writer.sheets[name]
        for col in ws.columns:
            w = max(len(str(c.value or "")) for c in col) + 3
            ws.column_dimensions[col[0].column_letter].width = min(w, 38)
conn.close()
print(f"  ✓ Excel → {excel_path}")

print("\n" + "=" * 62)
print("  PIPELINE COMPLETE")
print("=" * 62)
print(f"  Top revenue:  {top_revenue['company']} ${top_revenue['revenue_B']:.0f}B")
print(f"  Top margin:   {top_margin['company']} {top_margin['net_margin']:.1f}%")
print(f"  Best FCF:     {top_fcf['company']} ${top_fcf['fcf_B']:.0f}B")
print(f"  Charts:       {CHARTS}/  (6 files)")

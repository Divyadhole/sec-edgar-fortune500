"""
src/leverage_analysis.py
Debt and leverage analysis for Fortune 500 companies.

Key insight: Alphabet (Google) carries almost zero debt relative
to its size. Apple carries $111B debt — but generates $100B FCF,
so can repay entire debt in ~1 year.

Leverage tiers:
  Conservative:     D/E < 0.5
  Moderate:         D/E 0.5 - 1.5
  Leveraged:        D/E 1.5 - 3.0
  Highly Leveraged: D/E > 3.0
"""
from src.sec_data import load_financials

def run():
    df = load_financials()
    df23 = df[df["year"] == 2023].copy()
    df23["debt_to_fcf"] = (df23["total_debt_B"] /
                            df23["fcf_B"].replace(0, float("nan"))).round(1)

    print("LEVERAGE ANALYSIS — 2023")
    print("-" * 55)
    print(f"{'Company':<22} {'Debt($B)':<10} {'D/E':<8} {'Tier':<20} {'Debt/FCF'}")
    print("-" * 55)
    for _, row in df23.sort_values("debt_to_equity").iterrows():
        tier = ("Conservative" if row["debt_to_equity"] < 0.5 else
                "Moderate"    if row["debt_to_equity"] < 1.5 else
                "Leveraged"   if row["debt_to_equity"] < 3.0 else
                "High Leverage")
        dfcf = f"{row['debt_to_fcf']:.1f}x" if row["debt_to_fcf"] > 0 else "N/A"
        print(f"  {row['company']:<20} ${row['total_debt_B']:<9.0f} "
              f"{row['debt_to_equity']:<8.2f} {tier:<20} {dfcf}")

if __name__ == "__main__":
    run()

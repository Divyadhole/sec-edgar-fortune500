# Key Findings — SEC EDGAR Fortune 500 Analysis

## The 12-Company Snapshot (2023)
| Metric | Value |
|---|---|
| Combined Revenue | **$3.74 Trillion** |
| Combined Net Income | **$564 Billion** |
| Blended Net Margin | **15.1%** |
| Combined Free Cash Flow | **$522 Billion** |

---

## Finding 1: Walmart Has Revenue, Tech Has Margins

Walmart is the largest company by revenue ($611B) — more than
Apple and Microsoft combined. But Walmart's net margin is just 1.9%.

Microsoft earns **34.2 cents of profit for every dollar of revenue.**
Walmart earns **1.9 cents.**

This explains why Microsoft's market cap exceeds Walmart's despite
Walmart having more than 2x the revenue.

```
Revenue vs Profit Margin Gap:
  Walmart:   $611B revenue  |  1.9% margin  | $11.7B profit
  Microsoft: $212B revenue  | 34.2% margin  | $72.4B profit
```

---

## Finding 2: Apple Generates $100B in Free Cash Flow

Apple's free cash flow ($99.6B in 2023) exceeds the combined
free cash flow of the entire Energy sector in this dataset.

FCF is the truest measure of financial health — it's cash left
after all capital expenditures. Apple generates more cash than
most countries' GDP.

---

## Finding 3: Amazon's Growth vs Profitability Story

Amazon had the fastest revenue CAGR at **+19.6%/year** from 2019-2023.
But in 2022, Amazon posted a **$2.7B net loss** — despite $514B revenue.

The 2022 loss was driven by a $12.7B write-down on its Rivian investment.
By 2023 Amazon recovered to $30.4B profit.

Lesson: Revenue growth ≠ profit. Amazon proves you can have $500B+ revenue
and still post a loss.

---

## Finding 4: COVID Hit Energy Hardest, Tech Barely Noticed

2020 revenue change vs 2019:
- **Chevron**: -35.4% (oil demand collapsed)
- **ExxonMobil**: -32.6% (oil demand collapsed)
- **Microsoft**: +13.6% (remote work boom)
- **Amazon**: +37.6% (e-commerce surge)
- **Apple**: +5.5% (largely unaffected)

Energy companies depend on commodity prices — out of their control.
Tech companies benefited directly from the pandemic.

---

## Finding 5: Berkshire's 2022 "Loss" Was Not a Real Loss

Berkshire Hathaway reported a **$22.8B net loss in 2022.**
This terrified headlines. But operating profit was positive.

The "loss" was entirely due to GAAP accounting rules requiring
unrealized losses on their $300B+ equity portfolio to flow through
net income when markets fell in 2022.

By 2023 they reported $96.2B profit as markets recovered.
This is why Warren Buffett warns against using GAAP net income
to evaluate Berkshire.

---

## Data Source
SEC EDGAR XBRL API — no API key required, fully public.

All figures are from official 10-K annual filings submitted to
the Securities and Exchange Commission.

```python
# Verify any figure directly:
import requests
url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
data = requests.get(url, headers={"User-Agent": "Your Name email@domain.com"}).json()
# Navigate to: data["facts"]["us-gaap"]["Revenues"]["units"]["USD"]
```

URL: https://data.sec.gov/api/xbrl/companyfacts/

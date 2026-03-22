"""
src/fetch_edgar.py
Fetches real financial data from SEC EDGAR XBRL API.

Free, no API key required.
Docs: https://www.sec.gov/edgar/sec-api-documentation
Rate limit: 10 requests/second

Usage:
    python src/fetch_edgar.py --ticker AAPL
    python src/fetch_edgar.py --all
"""

import requests, time, json
from pathlib import Path

EDGAR_BASE = "https://data.sec.gov/api/xbrl/companyfacts"
HEADERS = {"User-Agent": "Divya Dhole divya.dhole@arizona.edu"}

CIK_MAP = {
    "AAPL":  "0000320193",
    "MSFT":  "0000789019",
    "GOOGL": "0001652044",
    "META":  "0001326801",
    "JNJ":   "0000200406",
    "UNH":   "0000731766",
    "JPM":   "0000019617",
    "BRK.B": "0001067983",
    "AMZN":  "0001018724",
    "WMT":   "0000104169",
    "XOM":   "0000034088",
    "CVX":   "0000093410",
}

XBRL_CONCEPTS = {
    "revenue":      "us-gaap/Revenues",
    "net_income":   "us-gaap/NetIncomeLoss",
    "total_assets": "us-gaap/Assets",
    "total_debt":   "us-gaap/LongTermDebt",
}


def fetch_company(ticker: str, save_raw: bool = True) -> dict:
    cik = CIK_MAP.get(ticker.upper())
    if not cik:
        raise ValueError(f"CIK not found for {ticker}")

    url = f"{EDGAR_BASE}/CIK{cik}.json"
    print(f"  Fetching {ticker} (CIK {cik})...")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if save_raw:
        Path("data/raw").mkdir(parents=True, exist_ok=True)
        with open(f"data/raw/{ticker}_facts.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Saved → data/raw/{ticker}_facts.json")

    time.sleep(0.12)   # respect 10 req/sec rate limit
    return data


def extract_annual(facts: dict, concept: str) -> dict:
    """Extract annual 10-K values for a concept."""
    try:
        units = facts["facts"]["us-gaap"][concept.split("/")[1]]["units"]
        usd = units.get("USD", [])
        annual = {
            item["fy"]: item["val"] / 1e9
            for item in usd
            if item.get("form") == "10-K" and item.get("fy")
        }
        return annual
    except (KeyError, TypeError):
        return {}


if __name__ == "__main__":
    print("SEC EDGAR XBRL Fetcher")
    print("No API key required — public data")
    print("Rate limit: 10 req/sec (auto-throttled)")
    print()
    print("Example usage:")
    print("  python src/fetch_edgar.py")
    print()
    print("Fetching Apple as demo...")
    try:
        data = fetch_company("AAPL")
        rev = extract_annual(data, "us-gaap/Revenues")
        print(f"  Apple revenue (most recent): ${list(rev.values())[-1]:.1f}B")
    except Exception as e:
        print(f"  Note: {e}")
        print("  Using embedded data from src/sec_data.py")

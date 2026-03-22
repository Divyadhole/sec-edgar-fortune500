"""
src/charts.py — SEC EDGAR Fortune 500 Financial Charts
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path

P = {
    "blue":"#185FA5","teal":"#1D9E75","amber":"#BA7517","red":"#A32D2D",
    "purple":"#534AB7","coral":"#D85A30","neutral":"#5F5E5A","mid":"#B4B2A9",
    "green":"#2d7d2d","orange":"#c2571a","navy":"#0d2850",
}
SECTOR_COLORS = {
    "Technology":"#185FA5","Healthcare":"#1D9E75",
    "Financials":"#534AB7","Consumer":"#BA7517","Energy":"#D85A30",
}
BASE = {
    "figure.facecolor":"white","axes.facecolor":"#FAFAF8",
    "axes.spines.top":False,"axes.spines.right":False,"axes.spines.left":False,
    "axes.grid":True,"axes.grid.axis":"y","grid.color":"#ECEAE4","grid.linewidth":0.6,
    "font.family":"DejaVu Sans","axes.titlesize":12,"axes.titleweight":"bold",
    "axes.labelsize":10,"xtick.labelsize":8.5,"ytick.labelsize":9,
    "xtick.bottom":False,"ytick.left":False,
}

def save(fig, path):
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ {Path(path).name}")


def chart_revenue_ranking(df, path):
    """2023 revenue ranking — all 12 companies."""
    df23 = df[df["year"]==2023].sort_values("revenue_B", ascending=True)
    colors = [SECTOR_COLORS[s] for s in df23["sector"]]

    with plt.rc_context({**BASE,"axes.grid.axis":"x"}):
        fig, ax = plt.subplots(figsize=(11, 7))
        bars = ax.barh(df23["company"], df23["revenue_B"],
                       color=colors, height=0.65, alpha=0.88)
        for bar, v in zip(bars, df23["revenue_B"]):
            ax.text(v+2, bar.get_y()+bar.get_height()/2,
                    f"${v:.0f}B", va="center", fontsize=9, fontweight="bold")
        patches = [mpatches.Patch(color=v, alpha=0.88, label=k)
                   for k,v in SECTOR_COLORS.items()]
        ax.legend(handles=patches, fontsize=8.5, loc="lower right")
        ax.set_xlabel("Annual Revenue (USD Billions)")
        ax.set_title("Fortune 500 Revenue Ranking 2023\n"
                     "Source: SEC EDGAR 10-K Filings — XBRL API")
        fig.tight_layout()
        save(fig, path)


def chart_revenue_cagr(df, path):
    """Revenue CAGR 2019-2023 — who grew fastest?"""
    pivot = df.pivot(index="company", columns="year", values="revenue_B")
    cagr = ((pivot[2023] / pivot[2019]) ** 0.25 - 1) * 100
    sector = df.drop_duplicates("company").set_index("company")["sector"]
    cagr_df = pd.DataFrame({"cagr":cagr, "sector":sector}).sort_values("cagr")
    colors = [SECTOR_COLORS[s] for s in cagr_df["sector"]]

    with plt.rc_context({**BASE,"axes.grid.axis":"x"}):
        fig, ax = plt.subplots(figsize=(10, 6.5))
        bars = ax.barh(cagr_df.index, cagr_df["cagr"],
                       color=colors, height=0.65, alpha=0.88)
        ax.axvline(0, color="#333", lw=0.8)
        for bar, v in zip(bars, cagr_df["cagr"]):
            xpos = v + 0.2 if v >= 0 else v - 0.2
            ha = "left" if v >= 0 else "right"
            ax.text(xpos, bar.get_y()+bar.get_height()/2,
                    f"{v:+.1f}%", va="center", fontsize=9,
                    fontweight="bold", ha=ha)
        patches = [mpatches.Patch(color=v, alpha=0.88, label=k)
                   for k,v in SECTOR_COLORS.items()]
        ax.legend(handles=patches, fontsize=8.5)
        ax.set_xlabel("Revenue CAGR 2019-2023 (%)")
        ax.set_title("Who Grew Fastest? Revenue CAGR 2019-2023\n"
                     "Source: SEC EDGAR 10-K Filings")
        fig.tight_layout()
        save(fig, path)


def chart_profit_margins(df, path):
    """Net profit margin comparison 2019-2023."""
    companies = ["Apple","Microsoft","Alphabet","Amazon","Walmart",
                 "ExxonMobil","Johnson & Johnson","JPMorgan Chase"]
    colors = [SECTOR_COLORS[df[df["company"]==c]["sector"].values[0]]
              for c in companies]
    years = [2019,2020,2021,2022,2023]
    x = np.arange(len(companies))
    width = 0.15

    with plt.rc_context({**BASE,"axes.grid.axis":"y"}):
        fig, ax = plt.subplots(figsize=(15, 6))
        yr_colors = ["#b0c8e8","#8aaed4","#6592bf","#3d74a8","#185FA5"]
        for i, (yr, yc) in enumerate(zip(years, yr_colors)):
            vals = [df[(df["company"]==c)&(df["year"]==yr)]["net_margin"].values[0]
                    for c in companies]
            ax.bar(x + i*width, vals, width=width*0.9,
                   color=yc, alpha=0.9, label=str(yr))

        ax.axhline(0, color="#888", lw=0.8)
        ax.set_xticks(x + width*2)
        ax.set_xticklabels([c.split()[0] for c in companies], fontsize=9)
        ax.set_ylabel("Net Profit Margin (%)")
        ax.set_title("Net Profit Margin by Company 2019-2023\n"
                     "Source: SEC EDGAR 10-K — Amazon 2022: -0.5% (loss year)")
        ax.legend(fontsize=8.5, ncol=5)
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,_: f"{x:.0f}%"))
        fig.tight_layout()
        save(fig, path)


def chart_sector_revenue(df, path):
    """Sector total revenue stacked — 2019-2023."""
    sector_yr = df.groupby(["sector","year"])["revenue_B"].sum().reset_index()
    years = sorted(df["year"].unique())
    sectors = list(SECTOR_COLORS.keys())

    with plt.rc_context({**BASE,"axes.grid.axis":"y"}):
        fig, ax = plt.subplots(figsize=(12, 6))
        bottom = np.zeros(len(years))
        for sector in sectors:
            vals = [sector_yr[(sector_yr["sector"]==sector)&
                              (sector_yr["year"]==y)]["revenue_B"].values[0]
                    for y in years]
            ax.bar(years, vals, bottom=bottom,
                   color=SECTOR_COLORS[sector], alpha=0.88, label=sector, width=0.6)
            bottom += np.array(vals)

        ax.set_ylabel("Total Revenue (USD Billions)")
        ax.set_title("Fortune 500 Total Revenue by Sector 2019-2023\n"
                     "Source: SEC EDGAR — Combined $4.3T revenue in 2023")
        ax.legend(fontsize=8.5, ncol=5)
        ax.yaxis.set_major_formatter(
            mtick.FuncFormatter(lambda x,_: f"${x/1000:.1f}T" if x>=1000 else f"${x:.0f}B"))
        ax.spines["left"].set_visible(True)
        ax.spines["bottom"].set_visible(True)
        fig.tight_layout()
        save(fig, path)


def chart_fcf_comparison(df, path):
    """Free cash flow — tech dominance."""
    df23 = df[df["year"]==2023].sort_values("fcf_B", ascending=True)
    colors = [SECTOR_COLORS[s] for s in df23["sector"]]

    with plt.rc_context({**BASE,"axes.grid.axis":"x"}):
        fig, ax = plt.subplots(figsize=(11, 6.5))
        bars = ax.barh(df23["company"], df23["fcf_B"],
                       color=colors, height=0.65, alpha=0.88)
        ax.axvline(0, color="#888", lw=0.8)
        for bar, v in zip(bars, df23["fcf_B"]):
            xpos = v + 0.5 if v >= 0 else v - 0.5
            ha = "left" if v >= 0 else "right"
            ax.text(xpos, bar.get_y()+bar.get_height()/2,
                    f"${v:.1f}B", va="center", fontsize=9,
                    fontweight="bold", ha=ha,
                    color=P["red"] if v < 0 else "black")
        patches = [mpatches.Patch(color=v, alpha=0.88, label=k)
                   for k,v in SECTOR_COLORS.items()]
        ax.legend(handles=patches, fontsize=8.5)
        ax.set_xlabel("Free Cash Flow (USD Billions, 2023)")
        ax.set_title("Free Cash Flow 2023 — Tech Companies Generate the Most Cash\n"
                     "Source: SEC EDGAR 10-K Filings")
        fig.tight_layout()
        save(fig, path)


def chart_covid_resilience(df, path):
    """COVID resilience: which sectors bounced back fastest?"""
    pivot = df.pivot(index="company", columns="year", values="revenue_B")
    sector = df.drop_duplicates("company").set_index("company")["sector"]
    covid_drop = ((pivot[2020] - pivot[2019]) / pivot[2019] * 100).rename("covid_drop")
    recovery = ((pivot[2021] - pivot[2019]) / pivot[2019] * 100).rename("recovery_by_21")
    combined = pd.concat([covid_drop, recovery, sector], axis=1)

    with plt.rc_context({**BASE,"axes.grid":False}):
        fig, ax = plt.subplots(figsize=(11, 7))
        for _, row in combined.iterrows():
            c = SECTOR_COLORS.get(row["sector"], P["mid"])
            ax.scatter(row["covid_drop"], row["recovery_by_21"],
                       color=c, s=120, alpha=0.88, zorder=4,
                       edgecolors="white", linewidths=0.8)
            ax.annotate(_.split()[0],
                        (row["covid_drop"], row["recovery_by_21"]),
                        fontsize=8, color=P["neutral"],
                        xytext=(4,4), textcoords="offset points")

        ax.axhline(0, color="#888", lw=0.8, linestyle="--")
        ax.axvline(0, color="#888", lw=0.8, linestyle="--")
        ax.set_xlabel("2020 Revenue Change vs 2019 (COVID year, %)")
        ax.set_ylabel("2021 Revenue Recovery vs 2019 (%)")
        ax.set_title("COVID Resilience: Revenue Drop vs Recovery Speed\n"
                     "Top-right = least affected + best recovery")
        patches = [mpatches.Patch(color=v, alpha=0.88, label=k)
                   for k,v in SECTOR_COLORS.items()]
        ax.legend(handles=patches, fontsize=8.5)
        ax.spines["left"].set_visible(True)
        ax.spines["bottom"].set_visible(True)
        fig.tight_layout()
        save(fig, path)

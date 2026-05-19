"""Medium (English) 投稿用に最適化したグラフを生成する。

note 用の note_fig*.png と同じデータ・構図を、英語ラベル + IG カラーパレット
(DejaVu Sans, ACCENT=#D32F2F) に揃えたバージョンとして書き出す。

- 出力先: blog/medium_acidity/med_fig{1..4}.png
- アスペクト比は note 版を踏襲（横長、本文幅にフィット）
- 蔵名はローマ字 (Tsuchida, Hiran, Fukucho, Aramasa, Senkin, Kazenomori, Jikon)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "blog" / "medium_acidity"
DATA = ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)

# Hiragino Sans を主役に。Latin・→・CJK すべて1フォントで描画できる。
plt.style.use("seaborn-v0_8-whitegrid")
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = [
    "Hiragino Sans", "DejaVu Sans", "Helvetica Neue", "Helvetica", "Arial"
]
matplotlib.rcParams["axes.unicode_minus"] = False
matplotlib.rcParams["axes.titlesize"] = 15
matplotlib.rcParams["axes.labelsize"] = 12
matplotlib.rcParams["xtick.labelsize"] = 11
matplotlib.rcParams["ytick.labelsize"] = 11
matplotlib.rcParams["legend.fontsize"] = 11

ACCENT = "#D32F2F"
ACCENT_LIGHT = "#FFCDD2"
NEUTRAL = "#1976D2"
NEUTRAL_LIGHT = "#BBDEFB"
INK = "#212121"
SUB = "#616161"

SAVE_KW = {"dpi": 110, "bbox_inches": "tight", "pil_kwargs": {"optimize": True}}


# =========================================================================
# Fig 1: Six taste-keyword categories, 2014 vs 2025
# =========================================================================
def fig1_six_categories() -> None:
    cats = ["Sweet", "Acidic", "Fruity", "Rich", "Light", "Dry"]
    v_2014 = [6.5, 7.2, 6.6, 12.0, 9.8, 7.7]
    v_2025 = [30.0, 27.5, 20.5, 23.4, 20.1, 13.3]
    ratios = [4.58, 3.82, 3.11, 1.95, 2.06, 1.74]

    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = np.arange(len(cats))
    h = 0.36

    colors_2025 = [ACCENT if c == "Acidic" else NEUTRAL for c in cats]
    colors_2014 = [ACCENT_LIGHT if c == "Acidic" else NEUTRAL_LIGHT for c in cats]

    ax.barh(y_pos - h / 2, v_2014, h, color=colors_2014, label="2014")
    ax.barh(y_pos + h / 2, v_2025, h, color=colors_2025, label="2025")

    for i, (v14, v25, r) in enumerate(zip(v_2014, v_2025, ratios)):
        ax.text(v14 + 0.4, y_pos[i] - h / 2, f"{v14:.1f}%",
                va="center", fontsize=10, color=SUB)
        weight = "bold" if cats[i] == "Acidic" else "normal"
        ax.text(v25 + 0.4, y_pos[i] + h / 2, f"{v25:.1f}%",
                va="center", fontsize=11, fontweight=weight, color=INK)
        ax.text(36.5, y_pos[i], f"×{r:.2f}", va="center", fontsize=12,
                fontweight="bold",
                color=ACCENT if cats[i] == "Acidic" else "#444")
    ax.text(36.5, -0.85, "growth", fontsize=11, fontweight="bold",
            va="center", color=SUB)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cats, fontsize=13, fontweight="bold")
    ax.set_xlabel("Mention rate in reviews (%)")
    ax.set_xlim(0, 41)
    ax.invert_yaxis()
    ax.set_title(
        "Six taste-keyword categories: 2014 → 2025\n"
        "“Acidic” grew +20.3pt (×3.82) — second only to “Sweet”"
    )
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.20),
              ncol=2, frameon=False)
    ax.grid(axis="y", alpha=0)
    plt.tight_layout()
    plt.savefig(OUT / "med_fig1_six_categories.png", **SAVE_KW)
    plt.close(fig)
    print("saved: med_fig1_six_categories.png")


# =========================================================================
# Fig 2: Four acid types growth
# =========================================================================
def fig2_acid_types() -> None:
    types = [
        "Lactic\n(round, creamy)",
        "Citric\n(sharp, citrus)",
        "Malic\n(juicy, fruity)",
        "Tartaric\n(wine-like)",
    ]
    colors = ["#E0AC69", "#FBC02D", "#7CB342", "#7B1FA2"]
    v_2014 = [0.12, 0.83, 0.12, 1.49]
    v_2026 = [2.50, 3.87, 0.40, 2.61]
    ratios = [21.0, 4.6, 3.4, 1.8]

    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    y_pos = np.arange(len(types))
    ax.barh(y_pos, ratios, color=colors, alpha=0.9, edgecolor="white",
            linewidth=1.4)

    max_ratio = max(ratios)
    for i, (r, v0, v1) in enumerate(zip(ratios, v_2014, v_2026)):
        if r >= max_ratio * 0.25:
            ax.text(r / 2, y_pos[i], f"×{r:.1f}",
                    va="center", ha="center", fontsize=20, fontweight="bold",
                    color="white")
            ax.text(r + max_ratio * 0.04, y_pos[i],
                    f"{v0:.2f}%  →  {v1:.2f}%",
                    va="center", fontsize=12, color=INK)
        else:
            ax.text(r + max_ratio * 0.04, y_pos[i],
                    f"×{r:.1f}    {v0:.2f}%  →  {v1:.2f}%",
                    va="center", fontsize=13, fontweight="bold", color=INK)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(types, fontsize=12)
    ax.set_xlabel("Growth multiplier (2014 → 2026)")
    ax.set_xlim(0, max_ratio * 1.55)
    ax.invert_yaxis()
    ax.set_title(
        "Four acid types tell four stories\n"
        "Lactic-acid vocabulary grew ×21 — the kimoto & yamahai revival shows up in language"
    )
    ax.grid(axis="y", alpha=0)
    plt.tight_layout()
    plt.savefig(OUT / "med_fig2_acid_types.png", **SAVE_KW)
    plt.close(fig)
    print("saved: med_fig2_acid_types.png")


# =========================================================================
# Fig 3: Brand × acid-type heatmap
# =========================================================================
def fig3_brand_profile() -> None:
    brands = [
        "Tsuchida 土田",
        "Hiran 飛鸞",
        "Fukucho 富久長",
        "Aramasa 新政",
        "Senkin 仙禽",
        "Kazenomori 風の森",
        "Jikon 而今",
        "All brands avg. 全銘柄平均",
    ]
    data = np.array(
        [
            [13.1, 4.6, 0.0, 5.1],
            [9.4, 13.5, 0.3, 3.7],
            [2.2, 8.6, 0.0, 4.7],
            [3.8, 8.5, 0.4, 6.5],
            [6.2, 7.1, 0.3, 5.4],
            [1.7, 3.0, 0.4, 4.1],
            [1.8, 1.5, 1.3, 1.1],
            [2.1, 3.2, 0.3, 2.9],
        ]
    )
    col_labels = [
        "Lactic\n(round)",
        "Citric\n(citrus)",
        "Malic\n(fruity)",
        "Tartaric\n(wine)",
    ]

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(
        data,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        xticklabels=col_labels,
        yticklabels=brands,
        cbar_kws={"label": "Mention rate (%)"},
        annot_kws={"size": 12, "weight": "bold"},
        linewidths=0.5,
        linecolor="white",
        ax=ax,
    )
    ax.set_title(
        "Brand × acid signature: each pioneer leans on a different acid\n"
        "(full-period average mention rate, %)",
        fontsize=13,
    )
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(OUT / "med_fig3_brand_profile.png", **SAVE_KW)
    plt.close(fig)
    print("saved: med_fig3_brand_profile.png")


# =========================================================================
# Fig 4: Google Trends time-series + multiplier bars
# =========================================================================
def fig4_google_trends() -> None:
    gt_path = DATA / "google_trends_acid_core.csv"
    gt = pd.read_csv(gt_path)
    gt["date"] = pd.to_datetime(gt["date"])
    gt["year"] = gt["date"].dt.year
    yt = gt.drop(columns=["date", "isPartial"]).groupby("year").mean()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5),
                             gridspec_kw={"width_ratios": [1.5, 1]})

    palette = {"生酛": "#388E3C", "白麹": "#FF6F00", "日本酒 酸味": "#1976D2"}
    en_label = {
        "生酛": "Kimoto",
        "白麹": "White koji",
        "日本酒 酸味": '"Sake acidity"',
    }
    for q in ["生酛", "白麹", "日本酒 酸味"]:
        if q in yt.columns:
            axes[0].plot(yt.index, yt[q], "o-", label=en_label[q],
                         linewidth=2.5, markersize=6, color=palette[q])
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Google search index (relative)")
    axes[0].set_title("Google Trends — monthly average by year", fontsize=12)
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3)

    queries = ["Kimoto", "White koji"]
    y_pos = np.arange(len(queries))
    ratios = [4.0, 2.2]
    abs_vals = [(17.6, 71.2), (25.2, 54.2)]
    colors = ["#388E3C", "#FF6F00"]
    axes[1].barh(y_pos, ratios, color=colors, alpha=0.9,
                 edgecolor="white", linewidth=1.4)
    for i, (r, (v0, v1)) in enumerate(zip(ratios, abs_vals)):
        axes[1].text(r / 2, y_pos[i], f"×{r:.1f}",
                     va="center", ha="center", fontsize=20, fontweight="bold",
                     color="white")
        axes[1].text(r + 0.1, y_pos[i], f"{v0:.0f} → {v1:.0f}",
                     va="center", fontsize=11, color=INK)
    axes[1].set_yticks(y_pos)
    axes[1].set_yticklabels(queries, fontsize=13, fontweight="bold")
    axes[1].set_xlim(0, 5.5)
    axes[1].set_xlabel("Search-volume multiplier (2014 → 2026)")
    axes[1].set_title("Growth by query", fontsize=12)
    axes[1].invert_yaxis()
    axes[1].grid(axis="y", alpha=0)

    fig.suptitle(
        "Google searches confirm the rise: consumers don't search for “acidity”,\n"
        "they search for the methods behind it — “kimoto” ×4.0, “white koji” ×2.2",
        fontsize=13, y=1.03,
    )
    plt.tight_layout()
    plt.savefig(OUT / "med_fig4_google_trends.png", **SAVE_KW)
    plt.close(fig)
    print("saved: med_fig4_google_trends.png")


# =========================================================================
# Fig 5: Three Worlds comparison (Dry vs Acidity)
# Medium で <table> がうまく取り込めなかった対策。横長スタイルで他の
# Medium 図 (fig1-4) と一貫させつつ、視認性を上げるために大きめフォント。
# =========================================================================
def fig5_three_worlds() -> None:
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # IG/note と同じパレット
    ACCENT_DRY = "#1976D2"
    ACCENT_ACID = "#D32F2F"
    BG_DRY = "#E3F2FD"
    BG_ACID = "#FFEBEE"
    ROW_LABEL = "#F5F5F5"
    BORDER = "#BBBBBB"
    INK = "#212121"
    SUB = "#555555"

    # Columns (axes coords)
    x_world = 0.025
    w_world = 0.17
    x_dry = x_world + w_world
    w_dry = 0.395
    x_acid = x_dry + w_dry
    w_acid = 0.385

    # Title block
    fig.text(0.5, 0.95, "Three Worlds, compared",
             ha="center", va="center", fontsize=24, fontweight="bold", color=INK)
    fig.text(0.5, 0.90, "Dry (previous piece)   vs   Acidity (this piece)",
             ha="center", va="center", fontsize=15, color=SUB)
    fig.text(0.5, 0.855,
             "Dry diverged by layer; acidity rises uniformly across all three layers.",
             ha="center", va="center", fontsize=12, color=SUB, fontstyle="italic")

    # Header row (axis labels for the two columns)
    header_y = 0.755
    header_h = 0.06
    ax.add_patch(mpatches.Rectangle(
        (x_dry, header_y), w_dry, header_h,
        facecolor=BG_DRY, edgecolor=BORDER, linewidth=1.2))
    ax.text(x_dry + w_dry / 2, header_y + header_h / 2,
            "Dry (previous piece)", ha="center", va="center",
            fontsize=17, fontweight="bold", color=ACCENT_DRY)
    ax.add_patch(mpatches.Rectangle(
        (x_acid, header_y), w_acid, header_h,
        facecolor=BG_ACID, edgecolor=BORDER, linewidth=1.2))
    ax.text(x_acid + w_acid / 2, header_y + header_h / 2,
            "Acidity (this piece)", ha="center", va="center",
            fontsize=17, fontweight="bold", color=ACCENT_ACID)

    # Data rows
    rows = [
        ("World 1\nTop-ranked\nbrands",
         "67% sweet / 4% dry\n— Discarded at the top",
         "CORE vocabulary 20.8%\nCORE ∪ RELATED > 30%\n— Unambiguously discussed"),
        ("World 2\nLower-ranked\nbrands",
         '28% sweet / 29% dry\n— Split, "dry" survives',
         "Close to the global average\n— Rises across all layers"),
        ("World 3\nGeneral consumer\nsearch",
         '"sake dry" 2.5× "sake sweet"\n— Survives in search',
         '"Acidity" not searched;\n"white koji" / "kimoto" 2–4×\n— Diffused via method names'),
    ]

    row_h = 0.225
    row_bottoms = [header_y - row_h * (i + 1) for i in range(len(rows))]

    for row_bottom, (world_label, dry_cell, acid_cell) in zip(row_bottoms, rows):
        row_center = row_bottom + row_h / 2

        # World label
        ax.add_patch(mpatches.Rectangle(
            (x_world, row_bottom), w_world, row_h,
            facecolor=ROW_LABEL, edgecolor=BORDER, linewidth=1.2))
        ax.text(x_world + w_world / 2, row_center, world_label,
                ha="center", va="center",
                fontsize=13, fontweight="bold", color=INK)

        # Dry cell
        ax.add_patch(mpatches.Rectangle(
            (x_dry, row_bottom), w_dry, row_h,
            facecolor="white", edgecolor=BORDER, linewidth=1.2))
        ax.text(x_dry + 0.012, row_center, dry_cell,
                ha="left", va="center", fontsize=13, color=INK)

        # Acidity cell
        ax.add_patch(mpatches.Rectangle(
            (x_acid, row_bottom), w_acid, row_h,
            facecolor="white", edgecolor=BORDER, linewidth=1.2))
        ax.text(x_acid + 0.012, row_center, acid_cell,
                ha="left", va="center", fontsize=13, color=INK)

    plt.savefig(OUT / "med_fig5_three_worlds.png", **SAVE_KW)
    plt.close(fig)
    print("saved: med_fig5_three_worlds.png")


if __name__ == "__main__":
    fig1_six_categories()
    fig2_acid_types()
    fig3_brand_profile()
    fig4_google_trends()
    fig5_three_worlds()
    print("\nDone.")

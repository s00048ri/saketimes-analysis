"""Instagram 用に最適化した英語版グラフを生成する。

note 用の note_fig*.png を、IG のフィード仕様 (1080×1080 正方形) と
英語表記に変換したスライドカルーセル用画像群として書き出す。

- 出力: blog/ig_acidity/ig{N}_*.png
- サイズ: 1080×1080 px (figsize=10×10, dpi=108)
- フォント: スマホ画面で読める大きさを優先
- ヘッドライン: スライドごとに 1 つのメッセージに絞る

スライド構成:
    ig1_cover      ── タイトル / 問い
    ig2_six_cats   ── 6カテゴリ 2014 vs 2025
    ig3_acid_types ── 4酸タイプ 21× 軸
    ig4_breweries  ── 蔵元 × 酸タイプ ヒートマップ
    ig5_trends     ── Google Trends 倍率
    ig6_outro      ── まとめスライド (full-text 誘導)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "blog" / "ig_acidity"
DATA = ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)

# IG portrait 4:5. 10in × 12.5in @ 108dpi = 1080×1350 px
FIGSIZE = (10, 12.5)
DPI = 108
SAVE_KW = {"dpi": DPI, "bbox_inches": "tight", "pil_kwargs": {"optimize": True}}
# カバー/アウトロは余白を残したまま正方形 1080×1080 にしたい (tight だと crop されるため)
SAVE_KW_FULL = {"dpi": DPI, "pil_kwargs": {"optimize": True}}

# Style
plt.style.use("seaborn-v0_8-whitegrid")
matplotlib.rcParams["font.family"] = "sans-serif"
# Hiragino Sans を主役に。Latin・→・CJK すべて1フォントで描画できるため、
# matplotlib の per-character font fallback (信頼性が低い) に頼らずに済む。
matplotlib.rcParams["font.sans-serif"] = [
    "Hiragino Sans", "DejaVu Sans", "Helvetica Neue", "Helvetica", "Arial"
]
matplotlib.rcParams["axes.unicode_minus"] = False

ACCENT = "#D32F2F"     # acidic / lactic story color
ACCENT_LIGHT = "#FFCDD2"
NEUTRAL = "#1976D2"
NEUTRAL_LIGHT = "#BBDEFB"
INK = "#212121"
SUB = "#616161"


# =========================================================================
# Slide 1: Cover — Acidity であることを最初の1秒で見せる構成
# =========================================================================
def ig1_cover() -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FAF8F4")

    # Eyebrow — small framing
    ax.text(0.5, 0.955, "D A T A   S T O R Y",
            ha="center", va="center", fontsize=13,
            color=ACCENT, fontweight="bold")

    # SAKE banner — make the topic obvious at a glance
    ax.text(0.5, 0.895, "JAPANESE SAKE",
            ha="center", va="center", fontsize=44,
            color=INK, fontweight="bold")
    ax.text(0.5, 0.842, "日本酒",
            ha="center", va="center", fontsize=22,
            color=SUB, family="Hiragino Sans")

    # Top divider
    ax.plot([0.22, 0.78], [0.795, 0.795], color="#CCCCCC", lw=1.2)

    # Setup question
    ax.text(0.5, 0.745, "What replaced",
            ha="center", va="center", fontsize=26,
            color=SUB, fontweight="normal")
    ax.text(0.5, 0.695, "“dry” sake?",
            ha="center", va="center", fontsize=26,
            color=SUB, fontweight="normal", fontstyle="italic")

    # Answer arrow
    ax.annotate(
        "", xy=(0.5, 0.595), xytext=(0.5, 0.655),
        arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=3,
                        mutation_scale=24),
    )

    # The Answer — huge, dominant
    ax.text(0.5, 0.49, "ACIDITY.",
            ha="center", va="center", fontsize=100,
            color=ACCENT, fontweight="bold")

    # Bilingual anchor
    ax.text(0.5, 0.385, "酸味",
            ha="center", va="center", fontsize=32,
            color=INK, fontweight="bold",
            family="Hiragino Sans")

    # Tagline
    ax.text(0.5, 0.295,
            "The quiet new pillar of\nmodern Japanese sake.",
            ha="center", va="center", fontsize=20,
            color=SUB, fontstyle="italic")

    # Bottom divider
    ax.plot([0.28, 0.72], [0.195, 0.195], color="#CCCCCC", lw=1.0)

    # Source bar
    ax.text(0.5, 0.148,
            "320,000+ SAKETIME reviews   ·   10 years",
            ha="center", va="center", fontsize=15,
            color=INK, fontweight="bold")
    ax.text(0.5, 0.112,
            "+ Google Trends 2014–2026",
            ha="center", va="center", fontsize=13, color=SUB)

    ax.text(0.5, 0.045, "Swipe →", ha="center", va="center",
            fontsize=20, color=ACCENT, fontweight="bold")

    plt.savefig(OUT / "ig1_cover.png", **SAVE_KW_FULL, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("saved: ig1_cover.png")


# =========================================================================
# Slide 2: 6 categories 2014 vs 2025
# =========================================================================
def ig2_six_categories() -> None:
    cats = ["Sweet", "Acidic", "Fruity", "Rich", "Light", "Dry"]
    v_2014 = [6.5, 7.2, 6.6, 12.0, 9.8, 7.7]
    v_2025 = [30.0, 27.5, 20.5, 23.4, 20.1, 13.3]
    ratios = [4.58, 3.82, 3.11, 1.95, 2.06, 1.74]

    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.patch.set_facecolor("white")

    y_pos = np.arange(len(cats))
    h = 0.38

    colors_2025 = [ACCENT if c == "Acidic" else NEUTRAL for c in cats]
    colors_2014 = [ACCENT_LIGHT if c == "Acidic" else NEUTRAL_LIGHT for c in cats]

    ax.barh(y_pos - h / 2, v_2014, h, color=colors_2014, label="2014")
    ax.barh(y_pos + h / 2, v_2025, h, color=colors_2025, label="2025")

    for i, (v14, v25, r) in enumerate(zip(v_2014, v_2025, ratios)):
        ax.text(v14 + 0.5, y_pos[i] - h / 2, f"{v14:.1f}%",
                va="center", fontsize=14, color=SUB)
        weight = "bold" if cats[i] == "Acidic" else "normal"
        ax.text(v25 + 0.5, y_pos[i] + h / 2, f"{v25:.1f}%",
                va="center", fontsize=16, fontweight=weight, color=INK)
        ax.text(40.5, y_pos[i], f"×{r:.2f}", va="center", fontsize=18,
                fontweight="bold",
                color=ACCENT if cats[i] == "Acidic" else "#444")

    ax.text(40.5, -0.85, "growth", fontsize=15, fontweight="bold",
            va="center", color=SUB)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cats, fontsize=20, fontweight="bold")
    ax.set_xlabel("Mention rate in reviews (%)", fontsize=15, color=SUB)
    ax.set_xlim(0, 45)
    ax.invert_yaxis()

    ax.set_title("Six taste-keyword categories\n2014 → 2025",
                 fontsize=26, fontweight="bold", pad=20, color=INK)

    ax.text(0.5, -0.12,
            "“Acidic” keywords grew 3.82× — second only to “Sweet”",
            transform=ax.transAxes, ha="center", fontsize=16,
            color=ACCENT, fontweight="bold")

    ax.legend(loc="lower right", fontsize=15, frameon=False)
    ax.grid(axis="y", alpha=0)
    ax.tick_params(axis="x", labelsize=13)

    plt.tight_layout()
    plt.savefig(OUT / "ig2_six_categories.png", **SAVE_KW)
    plt.close(fig)
    print("saved: ig2_six_categories.png")


# =========================================================================
# Slide 3: 4 acid types
# =========================================================================
def ig3_acid_types() -> None:
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

    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.patch.set_facecolor("white")

    y_pos = np.arange(len(types))
    ax.barh(y_pos, ratios, color=colors, alpha=0.9, edgecolor="white",
            linewidth=2)

    max_ratio = max(ratios)
    for i, (r, v0, v1) in enumerate(zip(ratios, v_2014, v_2026)):
        if r >= max_ratio * 0.25:
            ax.text(r / 2, y_pos[i], f"×{r:.1f}",
                    va="center", ha="center", fontsize=34, fontweight="bold",
                    color="white")
            ax.text(r + max_ratio * 0.04, y_pos[i],
                    f"{v0:.2f}%  →  {v1:.2f}%",
                    va="center", fontsize=16, color=INK)
        else:
            ax.text(r + max_ratio * 0.04, y_pos[i],
                    f"×{r:.1f}    {v0:.2f}%  →  {v1:.2f}%",
                    va="center", fontsize=18, fontweight="bold", color=INK)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(types, fontsize=17)
    ax.set_xlabel("Growth multiplier (2014 → 2026)", fontsize=15, color=SUB)
    ax.set_xlim(0, max_ratio * 1.55)
    ax.invert_yaxis()
    ax.grid(axis="y", alpha=0)
    ax.tick_params(axis="x", labelsize=13)

    ax.set_title("Four acids tell four stories\nLactic acid grew 21×",
                 fontsize=26, fontweight="bold", pad=20, color=INK)

    ax.text(0.5, -0.12,
            "Kimoto & yamahai revival drives lactic acid vocabulary",
            transform=ax.transAxes, ha="center", fontsize=15,
            color=SUB, fontstyle="italic")

    plt.tight_layout()
    plt.savefig(OUT / "ig3_acid_types.png", **SAVE_KW)
    plt.close(fig)
    print("saved: ig3_acid_types.png")


# =========================================================================
# Slide 4: Brewery × acid type heatmap
# =========================================================================
def ig4_breweries() -> None:
    brands = [
        "Tsuchida\n土田",
        "Hiran\n飛鸞",
        "Fukucho\n富久長",
        "Aramasa\n新政",
        "Senkin\n仙禽",
        "Kazenomori\n風の森",
        "Jikon\n而今",
        "All brands avg.\n全銘柄平均",
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
    col_labels = ["Lactic", "Citric", "Malic", "Tartaric"]

    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.patch.set_facecolor("white")

    sns.heatmap(
        data,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        xticklabels=col_labels,
        yticklabels=brands,
        cbar_kws={"label": "Mention rate (%)", "shrink": 0.7},
        annot_kws={"size": 20, "weight": "bold"},
        linewidths=0.8,
        linecolor="white",
        ax=ax,
    )
    ax.tick_params(axis="x", labelsize=18, rotation=0)
    # 蔵名は 2 行 (英 + 日) になるので少し小さく
    ax.tick_params(axis="y", labelsize=14, rotation=0)
    ax.figure.axes[-1].yaxis.label.set_size(14)
    ax.figure.axes[-1].tick_params(labelsize=12)

    ax.set_title(
        "Brand × acid signature\nEach pioneer leans on a different acid",
        fontsize=24, fontweight="bold", pad=22, color=INK,
    )

    ax.text(0.5, -0.10,
            "土田 = lactic   ·   富久長 / 飛鸞 = citric (white koji)",
            transform=ax.transAxes, ha="center", fontsize=14,
            color=SUB, fontstyle="italic")

    plt.tight_layout()
    plt.savefig(OUT / "ig4_breweries.png", **SAVE_KW)
    plt.close(fig)
    print("saved: ig4_breweries.png")


# =========================================================================
# Slide 5: Google Trends
# =========================================================================
def ig5_trends() -> None:
    gt_path = DATA / "google_trends_acid_core.csv"
    gt = pd.read_csv(gt_path)
    gt["date"] = pd.to_datetime(gt["date"])
    gt["year"] = gt["date"].dt.year
    yt = gt.drop(columns=["date", "isPartial"]).groupby("year").mean()

    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE,
                             gridspec_kw={"height_ratios": [1.2, 1]})
    fig.patch.set_facecolor("white")

    # Top: time-series
    palette = {"生酛": "#388E3C", "白麹": "#FF6F00", "日本酒 酸味": "#1976D2"}
    en_label = {
        "生酛": "Kimoto",
        "白麹": "White koji",
        "日本酒 酸味": '"Sake acidity"',
    }
    for q in ["生酛", "白麹", "日本酒 酸味"]:
        if q in yt.columns:
            axes[0].plot(yt.index, yt[q], "o-", label=en_label[q],
                         linewidth=3.5, markersize=10, color=palette[q])
    axes[0].set_xlabel("Year", fontsize=14, color=SUB)
    axes[0].set_ylabel("Google search index", fontsize=14, color=SUB)
    axes[0].set_title("Google search interest 2014–2026",
                      fontsize=20, fontweight="bold", color=INK, pad=12)
    axes[0].legend(fontsize=14, loc="upper left", frameon=True)
    axes[0].grid(True, alpha=0.3)
    axes[0].tick_params(labelsize=12)

    # Bottom: ratio bars
    queries = ["Kimoto", "White koji"]
    y_pos = np.arange(len(queries))
    ratios = [4.0, 2.2]
    abs_vals = [(17.6, 71.2), (25.2, 54.2)]
    colors = ["#388E3C", "#FF6F00"]
    axes[1].barh(y_pos, ratios, color=colors, alpha=0.9,
                 edgecolor="white", linewidth=2)
    for i, (r, (v0, v1)) in enumerate(zip(ratios, abs_vals)):
        axes[1].text(r / 2, y_pos[i], f"×{r:.1f}",
                     va="center", ha="center", fontsize=34, fontweight="bold",
                     color="white")
        axes[1].text(r + 0.1, y_pos[i], f"{v0:.0f} → {v1:.0f}",
                     va="center", fontsize=15, color=INK)
    axes[1].set_yticks(y_pos)
    axes[1].set_yticklabels(queries, fontsize=18, fontweight="bold")
    axes[1].set_xlim(0, 5.5)
    axes[1].set_xlabel("Search-volume multiplier (2014 → 2026)",
                       fontsize=14, color=SUB)
    axes[1].invert_yaxis()
    axes[1].grid(axis="y", alpha=0)
    axes[1].tick_params(axis="x", labelsize=12)

    fig.suptitle("Consumers don't search for “acidity”\nThey search for the methods behind it",
                 fontsize=22, fontweight="bold", y=1.00, color=INK)

    plt.tight_layout()
    plt.savefig(OUT / "ig5_trends.png", **SAVE_KW)
    plt.close(fig)
    print("saved: ig5_trends.png")


# =========================================================================
# Slide 6: Outro
# =========================================================================
def ig6_outro() -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FAF8F4")

    ax.text(0.5, 0.90, "T A K E A W A Y S", ha="center", va="center",
            fontsize=20, color=ACCENT, fontweight="bold")

    bullets = [
        ("01", "Acidity grew 3.82× in 10 years —",
               "second only to sweetness."),
        ("02", "Four organic acids, four stories.",
               "Lactic acid alone grew 21×."),
        ("03", "Each pioneer brand owns a",
               "different acid signature."),
        ("04", "Consumers search “kimoto” &",
               "“white koji”, not “acidity”."),
    ]

    y0 = 0.72
    for i, (n, l1, l2) in enumerate(bullets):
        y = y0 - i * 0.14
        ax.text(0.10, y, n, fontsize=34, fontweight="bold", color=ACCENT,
                va="center")
        ax.text(0.22, y + 0.025, l1, fontsize=20, color=INK,
                fontweight="bold", va="center")
        ax.text(0.22, y - 0.025, l2, fontsize=20, color=SUB, va="center")

    ax.text(0.5, 0.10,
            "Full article → link in bio",
            ha="center", va="center", fontsize=22,
            color=ACCENT, fontweight="bold")

    plt.savefig(OUT / "ig6_outro.png", **SAVE_KW_FULL, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("saved: ig6_outro.png")


if __name__ == "__main__":
    ig1_cover()
    ig2_six_categories()
    ig3_acid_types()
    ig4_breweries()
    ig5_trends()
    ig6_outro()
    print("\nDone.")

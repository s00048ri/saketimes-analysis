"""note 記事用に最適化した図を生成する。

article_jp_acidity.md のテーブルを置き換えるためのグラフを
blog/note_fig*.png に保存する。設計方針:

- 横長アスペクト比（note の本文幅に合う）
- 数値ラベルを大きく
- 主役（酸味・乳酸など）の色を強調
- 注釈で「倍率」「2014→2025の差分」を視覚的に伝える
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
DATA = ROOT / "data"

# note の表示幅 (~620px) に最適化。dpi=100 + コンパクト figsize で
# 1000px 幅前後にし、ファイルサイズを 40〜60KB に抑える。
SAVE_DPI = 100
SAVE_KW = {"dpi": SAVE_DPI, "bbox_inches": "tight", "pil_kwargs": {"optimize": True}}

# Global style
plt.style.use("seaborn-v0_8-whitegrid")
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Hiragino Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
matplotlib.rcParams["axes.titlesize"] = 15
matplotlib.rcParams["axes.labelsize"] = 12
matplotlib.rcParams["xtick.labelsize"] = 11
matplotlib.rcParams["ytick.labelsize"] = 11
matplotlib.rcParams["legend.fontsize"] = 11


# =========================================================================
# Fig 1: 6カテゴリ 2014 → 2025 の出現率比較
# =========================================================================
def fig1_six_categories() -> None:
    cats = ["甘口系", "酸味系", "フルーティ系", "芳醇系", "軽快系", "辛口系"]
    v_2014 = [6.5, 7.2, 6.6, 12.0, 9.8, 7.7]
    v_2025 = [30.0, 27.5, 20.5, 23.4, 20.1, 13.3]
    ratios = [4.58, 3.82, 3.11, 1.95, 2.06, 1.74]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    y_pos = np.arange(len(cats))
    h = 0.36

    # 酸味系を強調
    colors_2025 = [
        "#D32F2F" if c == "酸味系" else "#1976D2" for c in cats
    ]
    colors_2014 = [
        "#FFCDD2" if c == "酸味系" else "#BBDEFB" for c in cats
    ]

    bars_14 = ax.barh(y_pos - h / 2, v_2014, h, color=colors_2014, label="2014年")
    bars_25 = ax.barh(y_pos + h / 2, v_2025, h, color=colors_2025, label="2025年")

    for i, (v14, v25, r) in enumerate(zip(v_2014, v_2025, ratios)):
        ax.text(v14 + 0.4, y_pos[i] - h / 2, f"{v14:.1f}%",
                va="center", fontsize=10, color="#555")
        weight = "bold" if cats[i] == "酸味系" else "normal"
        ax.text(v25 + 0.4, y_pos[i] + h / 2, f"{v25:.1f}%",
                va="center", fontsize=11, fontweight=weight)
        # ratio at right
        ax.text(36, y_pos[i], f"× {r:.2f}", va="center", fontsize=11,
                fontweight="bold", color="#D32F2F" if cats[i] == "酸味系" else "#444")

    # ratio header
    ax.text(36, -0.85, "倍率", fontsize=11, fontweight="bold", va="center")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cats, fontsize=12)
    ax.set_xlabel("レビュー中の出現率 (%)")
    ax.set_xlim(0, 40)
    ax.invert_yaxis()
    ax.set_title("6カテゴリ味覚キーワードの出現率: 2014 → 2025\n酸味系は +20.3pt (3.82×) で甘口系に次ぐ伸び")
    ax.legend(loc="lower center", fontsize=11, bbox_to_anchor=(0.5, -0.18),
              ncol=2, frameon=False)
    ax.grid(axis="y", alpha=0)
    plt.tight_layout()
    plt.savefig(BLOG / "note_fig1_six_categories.png", **SAVE_KW)
    plt.close(fig)
    print("saved: note_fig1_six_categories.png")


# =========================================================================
# Fig 2: 4酸タイプの伸び倍率
# =========================================================================
def fig2_acid_types() -> None:
    types = [
        "乳酸系\n（丸み・まろやか）",
        "クエン酸系\n（シャープ・柑橘）",
        "リンゴ酸系\n（ジューシー・果実）",
        "酒石酸系\n（ワイン的）",
    ]
    colors = ["#E0AC69", "#FBC02D", "#7CB342", "#7B1FA2"]
    v_2014 = [0.12, 0.83, 0.12, 1.49]
    v_2026 = [2.50, 3.87, 0.40, 2.61]
    ratios = [21.0, 4.6, 3.4, 1.8]

    fig, ax = plt.subplots(figsize=(10, 5))
    y_pos = np.arange(len(types))
    bars = ax.barh(y_pos, ratios, color=colors, alpha=0.88, edgecolor="white",
                   linewidth=1.2)

    max_ratio = max(ratios)
    for i, (r, v0, v1) in enumerate(zip(ratios, v_2014, v_2026)):
        # ratio inside bar (if wide enough) or right outside it
        if r >= max_ratio * 0.25:
            ax.text(r / 2, y_pos[i], f"× {r:.1f}",
                    va="center", ha="center", fontsize=18, fontweight="bold",
                    color="white")
            ax.text(r + max_ratio * 0.04, y_pos[i],
                    f"{v0:.2f}%  →  {v1:.2f}%",
                    va="center", fontsize=11)
        else:
            ax.text(r + max_ratio * 0.04, y_pos[i],
                    f"× {r:.1f}    {v0:.2f}%  →  {v1:.2f}%",
                    va="center", fontsize=12, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(types, fontsize=11)
    ax.set_xlabel("出現率の倍率 (2014年 → 2026年)")
    ax.set_xlim(0, max_ratio * 1.55)
    ax.set_title("4つの酸タイプ別の伸び: 乳酸系が21倍で突出\nレビューに出てくる酸の語彙はタイプごとに別の物語を持つ")
    ax.invert_yaxis()
    ax.grid(axis="y", alpha=0)
    plt.tight_layout()
    plt.savefig(BLOG / "note_fig2_acid_types.png", **SAVE_KW)
    plt.close(fig)
    print("saved: note_fig2_acid_types.png")


# =========================================================================
# Fig 3: 蔵元 × 酸タイプ プロファイル
# =========================================================================
def fig3_brand_profile() -> None:
    brands = ["土田", "飛鸞", "富久長", "新政", "仙禽", "風の森", "而今", "全銘柄平均"]
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
    col_labels = ["乳酸系\n(丸み)", "クエン酸系\n(柑橘)", "リンゴ酸系\n(果実)", "酒石酸系\n(ワイン)"]

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    sns.heatmap(
        data,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        xticklabels=col_labels,
        yticklabels=brands,
        cbar_kws={"label": "出現率 (%)"},
        annot_kws={"size": 11},
        linewidths=0.5,
        linecolor="white",
        ax=ax,
    )
    ax.set_title("蔵元 × 酸タイプ プロファイル: 4蔵がそれぞれ異なる酸を得意とする\n（全銘柄平均と比較）",
                 fontsize=13)
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(BLOG / "note_fig3_brand_profile.png", **SAVE_KW)
    plt.close(fig)
    print("saved: note_fig3_brand_profile.png")


# =========================================================================
# Fig 4: Google Trends（時系列＋倍率の併置）
# =========================================================================
def fig4_google_trends() -> None:
    gt_path = DATA / "google_trends_acid_core.csv"
    gt = pd.read_csv(gt_path)
    gt["date"] = pd.to_datetime(gt["date"])
    gt["year"] = gt["date"].dt.year
    yt = gt.drop(columns=["date", "isPartial"]).groupby("year").mean()

    fig, axes = plt.subplots(1, 2, figsize=(11, 5),
                             gridspec_kw={"width_ratios": [1.5, 1]})

    # Left: time-series
    palette = {"生酛": "#388E3C", "白麹": "#FF6F00", "日本酒 酸味": "#1976D2"}
    for q in ["生酛", "白麹", "日本酒 酸味"]:
        if q in yt.columns:
            axes[0].plot(yt.index, yt[q], "o-", label=q, linewidth=2.5,
                         markersize=6, color=palette[q])
    axes[0].set_xlabel("年")
    axes[0].set_ylabel("Google 検索指数（相対）")
    axes[0].set_title("Google Trends 月次推移", fontsize=12)
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)

    # Right: ratio bars
    queries = ["生酛", "白麹"]
    y_pos = np.arange(len(queries))
    ratios = [4.0, 2.2]
    abs_vals = [(17.6, 71.2), (25.2, 54.2)]
    colors = [palette[q] for q in queries]
    bars = axes[1].barh(y_pos, ratios, color=colors, alpha=0.85,
                        edgecolor="white", linewidth=1.2)
    for i, (r, (v0, v1)) in enumerate(zip(ratios, abs_vals)):
        axes[1].text(r / 2, y_pos[i], f"× {r:.1f}",
                     va="center", ha="center", fontsize=18, fontweight="bold",
                     color="white")
        axes[1].text(r + 0.1, y_pos[i], f"{v0:.0f} → {v1:.0f}",
                     va="center", fontsize=10)
    axes[1].set_yticks(y_pos)
    axes[1].set_yticklabels(queries, fontsize=12)
    axes[1].set_xlim(0, 5.2)
    axes[1].set_xlabel("検索量の倍率 (2014 → 2026)")
    axes[1].set_title("クエリ別の伸び", fontsize=12)
    axes[1].invert_yaxis()
    axes[1].grid(axis="y", alpha=0)

    plt.suptitle("Google Trends も酸味系の台頭を裏付ける: 「生酛」4倍、「白麹」2.2倍",
                 fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig(BLOG / "note_fig4_google_trends.png", **SAVE_KW)
    plt.close(fig)
    print("saved: note_fig4_google_trends.png")


# =========================================================================
# Optional Fig 5: 「3つの世界」を可視化したミニ図
# =========================================================================
def fig5_three_worlds() -> None:
    worlds = ["世界1\nランキング上位 Top10", "世界2\n下位ランキング (501+)", "世界3\n一般消費者検索"]
    karakuchi = [4, 29, 71]   # 辛口の指標 (Top10/501+/Google「日本酒 辛口」/「日本酒 甘口」比 ≈ 2.5×なので相対値、ここでは71扱い)
    acid_pct = [25, 22, 71]   # CORE+RELATED率 → 生酛検索倍率の代理 (世界3は別単位なので注記)

    # NOTE: 世界3 だけ尺度が違う点を明示するため、図を分けるかキャプションで補足。
    # ここではシンプルに「酸味系の活性度」だけ並べる
    activity = [22.5, 21.0, 4.0]  # CORE出現率（Top10と501+）と、Google生酛検索の倍率(参考)
    labels = ["Top10 で CORE 22.5%", "501+ で CORE 21.0%", "「生酛」検索 4.0× 増"]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    colors = ["#D32F2F", "#FF8A65", "#388E3C"]
    bars = ax.bar(worlds, activity, color=colors, alpha=0.85,
                  edgecolor="white", linewidth=1.5)
    for i, (a, lbl) in enumerate(zip(activity, labels)):
        ax.text(i, a + 0.5, lbl, ha="center", fontsize=12, fontweight="bold")
    ax.set_ylabel("活性度（単位は世界ごとに異なる—注釈参照）")
    ax.set_ylim(0, 30)
    ax.set_title("3つの世界、酸味で揃う: レビュー上位・下位・検索すべて上昇",
                 fontsize=15)
    plt.tight_layout()
    plt.savefig(BLOG / "note_fig5_three_worlds.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved: note_fig5_three_worlds.png")


if __name__ == "__main__":
    fig1_six_categories()
    fig2_acid_types()
    fig3_brand_profile()
    fig4_google_trends()
    # fig5 はテーブル代替ではなく結語の補強用なので任意
    print("\nDone.")

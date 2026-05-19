"""note 投稿用のサムネイル (eyecatch / OG image) を生成する。

仕様:
    - 1280×670 px (note 推奨 1.91:1 横長)
    - IG カバーと視覚言語を統一: 赤 (#D32F2F), 太字 ACIDITY, 酸味アンカー
    - 左に文字組み、右に ×3.82 のデータコールアウト

出力:
    blog/article_jp_acidity_thumbnail.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "blog"

# 1280×670 at dpi=100 → figsize=(12.8, 6.7)
FIGSIZE = (12.8, 6.7)
DPI = 100

plt.style.use("seaborn-v0_8-whitegrid")
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = [
    "Hiragino Sans", "DejaVu Sans", "Helvetica Neue", "Helvetica", "Arial"
]
matplotlib.rcParams["axes.unicode_minus"] = False

ACCENT = "#D32F2F"
ACCENT_PALE = "#FFCDD2"
INK = "#212121"
SUB = "#616161"
BG = "#FAF8F4"


def make_thumbnail() -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor(BG)

    # ====== Vertical divider between text column and stat column ======
    DIV = 0.66  # 左 66% : 右 34%
    ax.plot([DIV, DIV], [0.18, 0.82], color="#D0D0D0", lw=1.0)

    # ============ Left column: title + tagline =============
    LEFT_X = 0.045

    # Eyebrow
    ax.text(LEFT_X, 0.90, "D A T A   S T O R Y   ·   日本酒",
            ha="left", va="center", fontsize=14,
            color=ACCENT, fontweight="bold")

    # Setup question
    ax.text(LEFT_X, 0.79, "What replaced",
            ha="left", va="center", fontsize=22,
            color=SUB, fontweight="normal")
    ax.text(LEFT_X, 0.72, "“dry” sake?",
            ha="left", va="center", fontsize=22,
            color=SUB, fontstyle="italic")

    # Big ACIDITY (slightly smaller so it doesn't crowd the divider)
    ax.text(LEFT_X, 0.49, "ACIDITY.",
            ha="left", va="center", fontsize=72,
            color=ACCENT, fontweight="bold")

    # 酸味 anchor
    ax.text(LEFT_X, 0.31, "酸味",
            ha="left", va="center", fontsize=32,
            color=INK, fontweight="bold")

    # Tagline
    ax.text(LEFT_X, 0.19,
            "The quiet new pillar of modern Japanese sake.",
            ha="left", va="center", fontsize=15,
            color=SUB, fontstyle="italic")

    # Source
    ax.text(LEFT_X, 0.09,
            "320,000+ SAKETIME reviews   ·   10 years   ·   Google Trends",
            ha="left", va="center", fontsize=12,
            color=INK, fontweight="bold")

    # ============ Right column: stat callout (no box, pure type) =====
    RIGHT_X = 0.835

    # Label above
    ax.text(RIGHT_X, 0.74, "ACIDITY GREW",
            ha="center", va="center", fontsize=14,
            color=SUB, fontweight="bold")

    # The number — dominant
    ax.text(RIGHT_X, 0.52, "×3.82",
            ha="center", va="center", fontsize=88,
            color=ACCENT, fontweight="bold")

    # Underline accent
    ax.plot([0.72, 0.95], [0.345, 0.345], color=ACCENT, lw=2.5)

    # Context lines
    ax.text(RIGHT_X, 0.29, "in 10 years",
            ha="center", va="center", fontsize=17,
            color=INK, fontweight="bold")
    ax.text(RIGHT_X, 0.22, "(2nd only to sweet)",
            ha="center", va="center", fontsize=12,
            color=SUB, fontstyle="italic")

    plt.savefig(
        OUT / "article_jp_acidity_thumbnail.png",
        dpi=DPI,
        facecolor=fig.get_facecolor(),
        pil_kwargs={"optimize": True},
    )
    plt.close(fig)
    print("saved: blog/article_jp_acidity_thumbnail.png")


if __name__ == "__main__":
    make_thumbnail()

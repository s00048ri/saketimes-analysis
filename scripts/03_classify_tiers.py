"""
Task 3: 3ティア分類

Top（定番の名酒）:
  - さけのわランキング上位 AND/OR SAKETIMEレビュー数 2,000+
  - 評価が安定的に高い

Middle（知る人ぞ知る逸品）:
  - レビュー数 200–2,000
  - 評価がTop tier平均以上
  - 一定の認知あり

Newcomer（注目のニューカマー）:
  - レビュー数 <500 だが評価が高い（4.3+）
  - Momentum score（直近3ヶ月のレビュー増加率）が上位10%

出力: data/processed/tier_classification.parquet
"""

import pandas as pd
import numpy as np
import re
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")


def parse_date(d):
    m = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", str(d))
    if m:
        return pd.Timestamp(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return pd.NaT


def compute_momentum(reviews_df):
    """各銘柄のmomentum score（直近3ヶ月 / 過去12ヶ月平均）を計算"""
    reviews = reviews_df.copy()
    reviews["date_parsed"] = reviews["date"].apply(parse_date)
    reviews = reviews.dropna(subset=["date_parsed"])

    latest_date = reviews["date_parsed"].max()
    cutoff_3m = latest_date - pd.DateOffset(months=3)
    cutoff_12m = latest_date - pd.DateOffset(months=12)

    recent_3m = reviews[reviews["date_parsed"] >= cutoff_3m].groupby("brand_id").size()
    past_12m = reviews[reviews["date_parsed"] >= cutoff_12m].groupby("brand_id").size()
    monthly_avg = past_12m / 12

    momentum = (recent_3m / monthly_avg.replace(0, np.nan)).dropna()
    # 3ヶ月分なので3で割って月単位にしてから比較
    momentum = momentum / 3

    return momentum


def classify():
    print("データ読み込み中...")
    merged = pd.read_parquet(os.path.join(PROCESSED_DIR, "merged_brands.parquet"))
    skt_only = pd.read_parquet(os.path.join(PROCESSED_DIR, "saketime_only.parquet"))
    reviews = pd.read_csv(os.path.join(DATA_DIR, "reviews.csv"))

    print(f"  統合マスタ: {len(merged)}銘柄")
    print(f"  SAKETIMEのみ: {len(skt_only)}銘柄")

    # SAKETIMEのみのデータも含めて全銘柄を対象にする
    # skt_onlyにはさけのわデータがないので空カラムを追加
    skt_only_extended = skt_only.copy()
    for col in ["snw_id", "snw_name", "snw_brewery", "snw_pref", "snw_ranking",
                "f1", "f2", "f3", "f4", "f5", "f6", "match_method", "match_score"]:
        if col not in skt_only_extended.columns:
            skt_only_extended[col] = np.nan
    if "flavor_tags" not in skt_only_extended.columns:
        skt_only_extended["flavor_tags"] = [[] for _ in range(len(skt_only_extended))]

    # カラム名を統一
    skt_only_extended = skt_only_extended.rename(columns={
        "skt_name": "skt_name", "skt_brewery": "skt_brewery",
    })

    # 結合
    all_brands = pd.concat([merged, skt_only_extended], ignore_index=True)
    print(f"  全銘柄: {len(all_brands)}")

    # === Momentum計算 ===
    print("\nMomentum score計算中...")
    momentum = compute_momentum(reviews)
    all_brands["momentum"] = all_brands["skt_id"].map(momentum)
    momentum_threshold = momentum.quantile(0.90) if len(momentum) > 0 else 999
    print(f"  Momentum計算完了: {all_brands['momentum'].notna().sum()}銘柄")
    print(f"  上位10%閾値: {momentum_threshold:.2f}")

    # === 分類ロジック ===
    print("\n分類中...")

    def classify_brand(row):
        rating = row.get("skt_rating", 0) or 0
        reviews_count = row.get("skt_reviews", 0) or 0
        snw_rank = row.get("snw_ranking")
        skt_rank = row.get("skt_rank", 9999) or 9999
        mom = row.get("momentum", 0) or 0

        # === レコメンド対象外（データ不足）===
        # レビュー10件未満 → 評価が信頼できない
        if reviews_count < 10:
            return "unranked", "レビュー不足"

        # === Top: 定番の名酒（50-100銘柄を想定）===
        if reviews_count >= 2000:
            return "top", f"レビュー数{int(reviews_count)}件"
        if pd.notna(snw_rank) and snw_rank <= 50:
            return "top", f"さけのわランキング{int(snw_rank)}位"
        if skt_rank <= 50 and rating >= 4.2:
            return "top", f"SAKETIME {int(skt_rank)}位(評価{rating})"
        if reviews_count >= 1000 and rating >= 4.0:
            return "top", f"レビュー{int(reviews_count)}件/評価{rating}"

        # === Newcomer: 注目のニューカマー（200-500銘柄を想定）===
        # レビュー少数だが評価が全体平均(3.18)より明確に高い
        if reviews_count < 500 and rating >= 4.0:
            return "newcomer", f"高評価{rating}(レビュー{int(reviews_count)}件)"
        if reviews_count < 200 and rating >= 3.5:
            return "newcomer", f"注目株(評価{rating}, レビュー{int(reviews_count)}件)"
        # 急成長中 + 評価が平均以上
        if mom >= momentum_threshold and reviews_count < 500 and rating >= 3.2:
            return "newcomer", f"急成長中(momentum={mom:.1f}, 評価{rating})"

        # === Middle: 知る人ぞ知る逸品（500-1000銘柄を想定）===
        if 200 <= reviews_count < 2000 and rating >= 3.5:
            return "middle", f"レビュー{int(reviews_count)}件/評価{rating}"
        if pd.notna(snw_rank) and snw_rank <= 100:
            return "middle", f"さけのわ{int(snw_rank)}位"
        if 51 <= skt_rank <= 300 and rating >= 3.5:
            return "middle", f"SAKETIME {int(skt_rank)}位"
        if reviews_count >= 50 and rating >= 3.3:
            return "middle", f"レビュー{int(reviews_count)}件/評価{rating}"

        # === その他 ===
        return "unranked", "分類基準未達"

    results = all_brands.apply(classify_brand, axis=1, result_type="expand")
    all_brands["tier"] = results[0]
    all_brands["tier_reason"] = results[1]

    # === 結果サマリー ===
    print(f"\n{'='*60}")
    print("分類結果")
    print(f"{'='*60}")
    tier_counts = all_brands["tier"].value_counts()
    for tier in ["top", "middle", "newcomer"]:
        count = tier_counts.get(tier, 0)
        tier_data = all_brands[all_brands["tier"] == tier]
        avg_rating = tier_data["skt_rating"].mean()
        avg_reviews = tier_data["skt_reviews"].mean()
        print(f"  {tier:>10}: {count:>5}銘柄  平均評価={avg_rating:.2f}  平均レビュー数={avg_reviews:.0f}")

    print(f"\n=== Top tier サンプル ===")
    top = all_brands[all_brands["tier"] == "top"].sort_values("skt_rank")
    for _, row in top.head(10).iterrows():
        name = row.get("snw_name") or row.get("skt_name", "?")
        print(f"  {name}: 評価{row['skt_rating']}, レビュー{int(row.get('skt_reviews',0))}件, {row['tier_reason']}")

    print(f"\n=== Newcomer tier サンプル ===")
    newcomer = all_brands[all_brands["tier"] == "newcomer"].sort_values("skt_rating", ascending=False)
    for _, row in newcomer.head(10).iterrows():
        name = row.get("snw_name") or row.get("skt_name", "?")
        print(f"  {name}: 評価{row['skt_rating']}, レビュー{int(row.get('skt_reviews',0))}件, {row['tier_reason']}")

    # 保存
    output_path = os.path.join(PROCESSED_DIR, "tier_classification.parquet")
    all_brands.to_parquet(output_path, index=False)
    print(f"\n保存: {output_path}")
    print(f"  行数: {len(all_brands)}, カラム数: {len(all_brands.columns)}")


if __name__ == "__main__":
    classify()

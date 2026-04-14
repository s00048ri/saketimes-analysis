"""
Task 2: さけのわ × SAKETIME 名寄せスクリプト

名寄せロジック:
1. 銘柄名の完全一致
2. 正規化後の一致（カッコ除去、全角半角統一）
3. 蔵元名での補助マッチ（銘柄名が類似 + 蔵元名一致）
4. fuzzy matching（rapidfuzz、閾値85以上）

出力: data/processed/merged_brands.parquet
"""

import json
import pandas as pd
import re
import os
import unicodedata
from rapidfuzz import fuzz, process

# === データ読み込み ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw", "sakenowa")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def load_sakenowa():
    with open(os.path.join(RAW_DIR, "brands.json")) as f:
        brands = json.load(f)["brands"]
    with open(os.path.join(RAW_DIR, "breweries.json")) as f:
        breweries = json.load(f)["breweries"]
    with open(os.path.join(RAW_DIR, "areas.json")) as f:
        areas = json.load(f)["areas"]
    with open(os.path.join(RAW_DIR, "rankings.json")) as f:
        rankings = json.load(f)
    with open(os.path.join(RAW_DIR, "flavor_charts.json")) as f:
        flavor_charts = json.load(f)["flavorCharts"]
    with open(os.path.join(RAW_DIR, "flavor_tags.json")) as f:
        flavor_tags = json.load(f)["tags"]
    with open(os.path.join(RAW_DIR, "brand_flavor_tags.json")) as f:
        brand_flavor_tags = json.load(f)["flavorTags"]

    brewery_map = {b["id"]: b for b in breweries}
    area_map = {a["id"]: a["name"] for a in areas}
    ranking_map = {r["brandId"]: r["rank"] for r in rankings["overall"]}
    fc_map = {fc["brandId"]: fc for fc in flavor_charts}
    tag_map = {t["id"]: t["tag"] for t in flavor_tags}
    bft_map = {bft["brandId"]: bft["tagIds"] for bft in brand_flavor_tags}

    records = []
    for b in brands:
        brewery = brewery_map.get(b["breweryId"], {})
        area_name = area_map.get(brewery.get("areaId"), "")
        fc = fc_map.get(b["id"], {})
        tag_ids = bft_map.get(b["id"], [])
        tags = [tag_map[tid] for tid in tag_ids if tid in tag_map]

        records.append({
            "snw_id": b["id"],
            "snw_name": b["name"],
            "snw_brewery": brewery.get("name", ""),
            "snw_pref": area_name,
            "snw_ranking": ranking_map.get(b["id"]),
            "f1": fc.get("f1"),
            "f2": fc.get("f2"),
            "f3": fc.get("f3"),
            "f4": fc.get("f4"),
            "f5": fc.get("f5"),
            "f6": fc.get("f6"),
            "flavor_tags": tags,
        })
    return pd.DataFrame(records)


def load_saketime():
    ranking = pd.read_csv(os.path.join(DATA_DIR, "ranking.csv"))
    brands = pd.read_csv(os.path.join(DATA_DIR, "brands.csv"))
    df = ranking.merge(brands[["brand_id", "brewery_name", "prefecture"]], on="brand_id", how="left")
    df = df.rename(columns={
        "brand_id": "skt_id",
        "name": "skt_name",
        "brewery_name": "skt_brewery",
        "prefecture": "skt_pref",
        "rank": "skt_rank",
        "rating": "skt_rating",
        "review_count": "skt_reviews",
    })
    return df


def normalize_name(name):
    """銘柄名の正規化"""
    if pd.isna(name):
        return ""
    s = str(name)
    # 全角→半角（英数字）
    s = unicodedata.normalize("NFKC", s)
    # カッコとその中身を除去
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    # 空白除去
    s = s.strip()
    # 小文字化（英語銘柄用）
    s = s.lower()
    return s


def normalize_brewery(name):
    """蔵元名の正規化"""
    if pd.isna(name):
        return ""
    s = str(name)
    s = unicodedata.normalize("NFKC", s)
    # 「株式会社」「有限会社」等を除去
    s = re.sub(r"(株式会社|有限会社|合資会社|合名会社|合同会社)", "", s)
    # 「酒造」「酒造店」「酒造場」「醸造」の揺れを統一
    s = s.strip()
    return s


def merge_sources():
    print("データ読み込み中...")
    snw = load_sakenowa()
    skt = load_saketime()
    print(f"  さけのわ: {len(snw)}銘柄")
    print(f"  SAKETIME: {len(skt)}銘柄")

    # 正規化カラム追加
    snw["name_norm"] = snw["snw_name"].apply(normalize_name)
    skt["name_norm"] = skt["skt_name"].apply(normalize_name)
    snw["brewery_norm"] = snw["snw_brewery"].apply(normalize_brewery)
    skt["brewery_norm"] = skt["skt_brewery"].apply(normalize_brewery)

    matched = []
    unmatched_snw = []
    used_skt_ids = set()

    # === Phase 1: 完全一致（銘柄名） ===
    print("\nPhase 1: 銘柄名の完全一致...")
    skt_by_name = skt.groupby("name_norm").apply(lambda x: x.to_dict("records")).to_dict()

    for _, row in snw.iterrows():
        candidates = skt_by_name.get(row["name_norm"], [])
        candidates = [c for c in candidates if c["skt_id"] not in used_skt_ids]

        if len(candidates) == 1:
            matched.append({**row.to_dict(), **candidates[0], "match_method": "exact", "match_score": 100})
            used_skt_ids.add(candidates[0]["skt_id"])
        elif len(candidates) > 1:
            # 蔵元名でさらに絞り込み
            brewery_match = [c for c in candidates if normalize_brewery(c.get("skt_brewery", "")) == row["brewery_norm"]]
            if len(brewery_match) == 1:
                matched.append({**row.to_dict(), **brewery_match[0], "match_method": "exact+brewery", "match_score": 100})
                used_skt_ids.add(brewery_match[0]["skt_id"])
            elif len(brewery_match) > 1:
                # 複数候補 → ランキング上位を選択
                best = min(brewery_match, key=lambda c: c.get("skt_rank", 99999))
                matched.append({**row.to_dict(), **best, "match_method": "exact+brewery+rank", "match_score": 100})
                used_skt_ids.add(best["skt_id"])
            else:
                unmatched_snw.append(row)
        else:
            unmatched_snw.append(row)

    print(f"  Phase 1 マッチ: {len(matched)}")

    # === Phase 2: Fuzzy matching ===
    print(f"\nPhase 2: Fuzzy matching（残り{len(unmatched_snw)}銘柄）...")
    remaining_skt = skt[~skt["skt_id"].isin(used_skt_ids)].copy()
    skt_names_list = remaining_skt["name_norm"].tolist()
    skt_ids_list = remaining_skt["skt_id"].tolist()

    phase2_matched = 0
    still_unmatched = []

    for row in unmatched_snw:
        if isinstance(row, pd.Series):
            row = row.to_dict()

        result = process.extractOne(
            row["name_norm"],
            skt_names_list,
            scorer=fuzz.ratio,
            score_cutoff=85
        )

        if result:
            match_name, score, idx = result
            skt_id = skt_ids_list[idx]
            if skt_id not in used_skt_ids:
                skt_row = remaining_skt[remaining_skt["skt_id"] == skt_id].iloc[0].to_dict()
                matched.append({**row, **skt_row, "match_method": "fuzzy", "match_score": score})
                used_skt_ids.add(skt_id)
                phase2_matched += 1
            else:
                still_unmatched.append(row)
        else:
            still_unmatched.append(row)

    print(f"  Phase 2 マッチ: {phase2_matched}")

    # === Phase 3: 蔵元名一致 + 緩いfuzzy ===
    print(f"\nPhase 3: 蔵元名一致 + 緩いfuzzy（残り{len(still_unmatched)}銘柄）...")
    remaining_skt2 = skt[~skt["skt_id"].isin(used_skt_ids)].copy()
    phase3_matched = 0
    final_unmatched = []

    for row in still_unmatched:
        # 同じ蔵元のSAKETIME銘柄を探す
        same_brewery = remaining_skt2[remaining_skt2["brewery_norm"] == row["brewery_norm"]]
        if len(same_brewery) == 0:
            final_unmatched.append(row)
            continue

        result = process.extractOne(
            row["name_norm"],
            same_brewery["name_norm"].tolist(),
            scorer=fuzz.ratio,
            score_cutoff=60
        )

        if result:
            match_name, score, idx = result
            skt_row = same_brewery.iloc[idx].to_dict()
            if skt_row["skt_id"] not in used_skt_ids:
                matched.append({**row, **skt_row, "match_method": "brewery+fuzzy", "match_score": score})
                used_skt_ids.add(skt_row["skt_id"])
                phase3_matched += 1
            else:
                final_unmatched.append(row)
        else:
            final_unmatched.append(row)

    print(f"  Phase 3 マッチ: {phase3_matched}")

    # === 結果まとめ ===
    total_matched = len(matched)
    print(f"\n{'='*60}")
    print(f"名寄せ結果")
    print(f"{'='*60}")
    print(f"  さけのわ全銘柄: {len(snw)}")
    print(f"  マッチ成功: {total_matched} ({total_matched/len(snw)*100:.1f}%)")
    print(f"  未マッチ: {len(final_unmatched)} ({len(final_unmatched)/len(snw)*100:.1f}%)")
    print(f"\n  方法別内訳:")

    method_counts = {}
    for m in matched:
        method = m["match_method"]
        method_counts[method] = method_counts.get(method, 0) + 1
    for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
        print(f"    {method}: {count}")

    # DataFrameに変換
    df = pd.DataFrame(matched)

    # カラム整理
    output_cols = [
        "snw_id", "skt_id", "snw_name", "skt_name",
        "snw_brewery", "skt_brewery", "snw_pref", "skt_pref",
        "snw_ranking", "skt_rank", "skt_rating", "skt_reviews",
        "f1", "f2", "f3", "f4", "f5", "f6",
        "flavor_tags",
        "match_method", "match_score"
    ]
    existing_cols = [c for c in output_cols if c in df.columns]
    df = df[existing_cols]

    # Parquet保存
    output_path = os.path.join(PROCESSED_DIR, "merged_brands.parquet")
    df.to_parquet(output_path, index=False)
    print(f"\n保存: {output_path}")
    print(f"  行数: {len(df)}, カラム数: {len(df.columns)}")

    # SAKETIMEのみ（さけのわに未登録）のデータも保存
    skt_only = skt[~skt["skt_id"].isin(used_skt_ids)].copy()
    skt_only_path = os.path.join(PROCESSED_DIR, "saketime_only.parquet")
    skt_only.to_parquet(skt_only_path, index=False)
    print(f"\nSAKETIMEのみ: {len(skt_only)}銘柄 → {skt_only_path}")

    # マッチ品質サンプル
    print(f"\n=== fuzzyマッチのサンプル（品質確認）===")
    fuzzy_matches = [m for m in matched if m["match_method"] in ("fuzzy", "brewery+fuzzy")]
    fuzzy_matches.sort(key=lambda x: x["match_score"])
    for m in fuzzy_matches[:10]:
        print(f"  [{m['match_score']:.0f}] {m['snw_name']} ↔ {m['skt_name']}  ({m['match_method']})")

    return df


if __name__ == "__main__":
    merge_sources()

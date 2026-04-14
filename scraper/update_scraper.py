"""
SAKETIME差分更新スクレイパー
既存データに対して新規追加分のみを取得する。

機能:
1. ランキングを再取得し、新規銘柄を検出
2. 新規銘柄の詳細情報を取得
3. 全銘柄の新着レビュー（前回取得時の最新日付以降）を取得
4. 既存CSVに追記（重複チェック付き）

使い方:
  python scraper/update_scraper.py              # 全処理を実行
  python scraper/update_scraper.py --ranking    # ランキングのみ更新
  python scraper/update_scraper.py --reviews    # レビューのみ更新
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import os
import re
import sys
import argparse
from datetime import datetime

# 既存スクレイパーからインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ranking_scraper import scrape_ranking_page, extract_brand_id
from brand_scraper import scrape_brand_page
from review_scraper import parse_reviews, has_next_page

BASE_URL = "https://www.saketime.jp/brands/"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}
DELAY = 2  # 差分更新は余裕を持って2秒間隔


def load_existing_ranking():
    """既存のranking.csvを読み込み"""
    path = os.path.join(DATA_DIR, "ranking.csv")
    if not os.path.exists(path):
        return []
    import pandas as pd
    return pd.read_csv(path).to_dict("records")


def load_existing_brand_ids():
    """既存のbrands.csvからbrand_idのセットを返す"""
    path = os.path.join(DATA_DIR, "brands.csv")
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {int(row["brand_id"]) for row in reader}


def get_latest_review_dates():
    """各銘柄の最新レビュー日付を取得"""
    path = os.path.join(DATA_DIR, "reviews.csv")
    if not os.path.exists(path):
        return {}
    latest = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bid = int(row["brand_id"])
            date_str = row.get("date", "")
            if date_str:
                if bid not in latest or date_str > latest[bid]:
                    latest[bid] = date_str
    return latest


def parse_date_str(d):
    """'2024年6月23日' -> datetime"""
    m = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", str(d))
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def update_ranking():
    """ランキングを再取得し、ranking.csvを上書き更新"""
    print("=" * 50)
    print("ランキング更新")
    print("=" * 50)

    old_ranking = load_existing_ranking()
    old_ids = {r["brand_id"] for r in old_ranking}

    all_brands = []
    page = 1
    while True:
        print(f"  ページ {page} 取得中...", end=" ")
        try:
            brands = scrape_ranking_page(page)
        except Exception as e:
            print(f"エラー: {e}")
            break
        if not brands:
            print("データなし - 終了")
            break
        all_brands.extend(brands)
        print(f"{len(brands)}銘柄取得 (累計: {len(all_brands)})")
        if len(brands) < 50:
            break
        page += 1
        time.sleep(DELAY)

    if not all_brands:
        print("ランキングデータが取得できませんでした")
        return [], []

    # 新規銘柄の検出
    new_ids = {b["brand_id"] for b in all_brands}
    added = new_ids - old_ids
    removed = old_ids - new_ids
    if added:
        print(f"  新規銘柄: {len(added)}件")
    if removed:
        print(f"  ランキング外: {len(removed)}件")

    # CSV上書き保存
    output = os.path.join(DATA_DIR, "ranking.csv")
    fieldnames = ["rank", "name", "brand_id", "url", "rating", "review_count", "description", "image_url"]
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_brands)
    print(f"  ranking.csv 更新完了: {len(all_brands)}銘柄")

    return list(added), all_brands


def update_brands(new_brand_ids):
    """新規銘柄の詳細情報を取得しbrands.csvに追記"""
    if not new_brand_ids:
        print("\n新規銘柄なし - スキップ")
        return

    print(f"\n{'=' * 50}")
    print(f"新規銘柄の詳細取得: {len(new_brand_ids)}件")
    print("=" * 50)

    fieldnames = [
        "brand_id", "brewery_name", "prefecture", "address",
        "brewery_description", "brewery_brands", "brewery_hp",
        "detail_rating", "min_price", "max_price", "rice_types",
        "prefecture_from_breadcrumb"
    ]

    output = os.path.join(DATA_DIR, "brands.csv")
    with open(output, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for i, bid in enumerate(new_brand_ids, 1):
            print(f"  [{i}/{len(new_brand_ids)}] brand_id={bid}...", end=" ")
            try:
                data = scrape_brand_page(bid)
                writer.writerow({k: data.get(k, "") for k in fieldnames})
                f.flush()
                print(f"OK - {data.get('brewery_name', '?')}")
            except Exception as e:
                print(f"エラー: {e}")
            time.sleep(DELAY)


def update_reviews(all_brands=None):
    """各銘柄の新着レビューを取得しreviews.csvに追記"""
    print(f"\n{'=' * 50}")
    print("新着レビュー取得")
    print("=" * 50)

    # 銘柄リストの読み込み
    if all_brands is None:
        ranking_path = os.path.join(DATA_DIR, "ranking.csv")
        if not os.path.exists(ranking_path):
            print("ranking.csvが見つかりません")
            return
        import pandas as pd
        all_brands = pd.read_csv(ranking_path).to_dict("records")

    # 各銘柄の最新レビュー日付を取得
    latest_dates = get_latest_review_dates()
    print(f"  既存レビューの最新日付データ: {len(latest_dates)}銘柄")

    fieldnames = [
        "brand_id", "username", "rating", "comment", "date",
        "specific_name", "rice", "sake_type", "body", "sweetness"
    ]

    output = os.path.join(DATA_DIR, "reviews.csv")
    total_new = 0

    with open(output, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        for i, brand in enumerate(all_brands, 1):
            bid = brand["brand_id"]
            name = brand["name"]
            cutoff_str = latest_dates.get(bid)
            cutoff_date = parse_date_str(cutoff_str) if cutoff_str else None

            # ページを順に取得し、cutoff_dateより前のレビューが出たら停止
            page = 1
            brand_new = 0
            stop = False

            while not stop:
                if page == 1:
                    url = f"{BASE_URL}{bid}/"
                else:
                    url = f"{BASE_URL}{bid}/page:{page}/"

                try:
                    resp = requests.get(url, headers=HEADERS)
                    resp.raise_for_status()
                except Exception as e:
                    break

                soup = BeautifulSoup(resp.text, "lxml")
                reviews = parse_reviews(soup, bid)

                if not reviews:
                    break

                for review in reviews:
                    review_date = parse_date_str(review.get("date", ""))
                    if cutoff_date and review_date and review_date <= cutoff_date:
                        stop = True
                        break
                    writer.writerow({k: review.get(k, "") for k in fieldnames})
                    brand_new += 1

                if not has_next_page(soup, bid, page):
                    break

                page += 1
                time.sleep(DELAY)

            if brand_new > 0:
                total_new += brand_new
                f.flush()
                print(f"  [{i}/{len(all_brands)}] {name}: +{brand_new}件 (累計新着: {total_new})")
            elif i % 500 == 0:
                print(f"  [{i}/{len(all_brands)}] 進行中... (累計新着: {total_new})")

    print(f"\n  新着レビュー合計: {total_new}件追加")


def main():
    parser = argparse.ArgumentParser(description="SAKETIME差分更新スクレイパー")
    parser.add_argument("--ranking", action="store_true", help="ランキングのみ更新")
    parser.add_argument("--reviews", action="store_true", help="レビューのみ更新")
    args = parser.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    start = datetime.now()
    print(f"差分更新開始: {start.strftime('%Y-%m-%d %H:%M:%S')}")

    if args.ranking:
        update_ranking()
    elif args.reviews:
        update_reviews()
    else:
        # 全処理
        new_brand_ids, all_brands = update_ranking()
        update_brands(new_brand_ids)
        update_reviews(all_brands)

    elapsed = datetime.now() - start
    print(f"\n完了: {elapsed}")


if __name__ == "__main__":
    main()

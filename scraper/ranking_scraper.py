"""
SAKETIMEランキングページから全銘柄の基本情報を取得するスクレイパー
URL: https://www.saketime.jp/ranking/page:{1-150}/
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import os
import re

BASE_URL = "https://www.saketime.jp/ranking/"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "ranking.csv")
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
DELAY = 1  # seconds between requests


def extract_brand_id(url):
    """URLからbrand IDを抽出: /brands/241/ -> 241"""
    match = re.search(r"/brands/(\d+)/", url)
    return int(match.group(1)) if match else None


def scrape_ranking_page(page_num):
    """1ページ分のランキングデータを取得"""
    if page_num == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}page:{page_num}/"

    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # JSON-LDからItemListを取得
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        data = json.loads(script.string)
        if data.get("@type") == "ItemList":
            items = data.get("itemListElement", [])
            results = []
            for item in items:
                product = item.get("item", {})
                rating = product.get("aggregateRating", {})
                # ページ内のpositionをグローバル順位に変換
                global_rank = (page_num - 1) * 50 + item["position"]
                results.append({
                    "rank": global_rank,
                    "name": product.get("name", ""),
                    "brand_id": extract_brand_id(product.get("url", "")),
                    "url": product.get("url", ""),
                    "rating": rating.get("ratingValue"),
                    "review_count": rating.get("reviewCount"),
                    "description": product.get("description", ""),
                    "image_url": product.get("image", ""),
                })
            return results
    return []


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    all_brands = []
    page = 1

    print("SAKETIMEランキング スクレイピング開始")
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

        # 最終ページ判定: 50件未満ならば最終ページ
        if len(brands) < 50:
            print("最終ページに到達")
            break

        page += 1
        time.sleep(DELAY)

    # CSV出力
    if all_brands:
        fieldnames = ["rank", "name", "brand_id", "url", "rating", "review_count", "description", "image_url"]
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_brands)
        print(f"\n完了: {len(all_brands)}銘柄を {OUTPUT_FILE} に保存")
    else:
        print("データが取得できませんでした")


if __name__ == "__main__":
    main()

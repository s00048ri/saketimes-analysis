"""
SAKETIME銘柄詳細ページから蔵元・地域情報を取得するスクレイパー
URL: https://www.saketime.jp/brands/{id}/
入力: data/ranking.csv (brand_idカラム)
出力: data/brands.csv
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import os
import re
import sys

BASE_URL = "https://www.saketime.jp/brands/"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RANKING_FILE = os.path.join(DATA_DIR, "ranking.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "brands.csv")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}
DELAY = 1


def extract_prefecture(address):
    """住所から都道府県を抽出"""
    match = re.match(r"(東京都|北海道|(?:京都|大阪)府|.{2,3}県)", address)
    return match.group(1) if match else ""


def scrape_brand_page(brand_id):
    """銘柄詳細ページから情報を取得"""
    url = f"{BASE_URL}{brand_id}/"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    result = {"brand_id": brand_id}

    # パンくずリストから都道府県リンクを取得
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if data.get("@type") == "BreadcrumbList":
                for item in data.get("itemListElement", []):
                    item_url = item.get("item", "")
                    if "/ranking/" in item_url and item_url != "https://www.saketime.jp/ranking/":
                        result["prefecture_from_breadcrumb"] = item.get("name", "").replace("の日本酒", "")
        except (json.JSONDecodeError, TypeError):
            pass

    # 蔵元情報テーブル
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if key == "名称":
                    result["brewery_name"] = value
                elif key == "所在地":
                    result["address"] = value
                    result["prefecture"] = extract_prefecture(value)
                elif key == "特徴":
                    result["brewery_description"] = value
                elif key == "銘柄":
                    result["brewery_brands"] = value
                elif key == "HP":
                    hp_link = cells[1].find("a")
                    result["brewery_hp"] = hp_link["href"] if hp_link else ""

    # 総合評価
    big_score = soup.find("span", class_="big-score")
    if big_score:
        parent_text = big_score.parent.get_text(strip=True)
        try:
            result["detail_rating"] = float(parent_text)
        except ValueError:
            pass

    # 商品テーブル（銘柄一覧）から価格帯を取得
    prices = []
    for table in tables:
        for cell in table.find_all("td"):
            text = cell.get_text(strip=True)
            price_matches = re.findall(r"¥([\d,]+)", text)
            for p in price_matches:
                try:
                    prices.append(int(p.replace(",", "")))
                except ValueError:
                    pass
    if prices:
        result["min_price"] = min(prices)
        result["max_price"] = max(prices)

    # 商品テーブルから原料米の種類を集める
    rice_types = set()
    for table in tables:
        for cell in table.find_all("td"):
            text = cell.get_text(strip=True)
            rice_match = re.search(r"原料米：([^、,，]+(?:[、,，][^、,，]+)*)", text)
            if rice_match:
                for rice in re.split(r"[、,，]", rice_match.group(1)):
                    rice = rice.strip()
                    if rice:
                        rice_types.add(rice)
    if rice_types:
        result["rice_types"] = "｜".join(sorted(rice_types))

    # prefectureが取れなかった場合、breadcrumbから補完
    if not result.get("prefecture") and result.get("prefecture_from_breadcrumb"):
        result["prefecture"] = result["prefecture_from_breadcrumb"]

    return result


def load_existing_brand_ids():
    """既に取得済みのbrand_idを返す（再開機能用）"""
    if not os.path.exists(OUTPUT_FILE):
        return set()
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {int(row["brand_id"]) for row in reader}


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # ranking.csvからbrand_idリストを読み込み
    if not os.path.exists(RANKING_FILE):
        print(f"エラー: {RANKING_FILE} が見つかりません。先にranking_scraper.pyを実行してください。")
        sys.exit(1)

    with open(RANKING_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        brand_ids = [int(row["brand_id"]) for row in reader if row["brand_id"]]

    print(f"対象銘柄数: {len(brand_ids)}")

    # 再開機能: 既に取得済みのIDをスキップ
    existing_ids = load_existing_brand_ids()
    remaining_ids = [bid for bid in brand_ids if bid not in existing_ids]
    if existing_ids:
        print(f"取得済み: {len(existing_ids)}件、残り: {len(remaining_ids)}件")

    fieldnames = [
        "brand_id", "brewery_name", "prefecture", "address",
        "brewery_description", "brewery_brands", "brewery_hp",
        "detail_rating", "min_price", "max_price", "rice_types",
        "prefecture_from_breadcrumb"
    ]

    # 追記モードで開く（再開対応）
    write_header = not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) == 0
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        for i, brand_id in enumerate(remaining_ids, 1):
            print(f"  [{i}/{len(remaining_ids)}] brand_id={brand_id} 取得中...", end=" ")
            try:
                data = scrape_brand_page(brand_id)
                writer.writerow({k: data.get(k, "") for k in fieldnames})
                f.flush()
                print(f"OK - {data.get('brewery_name', '?')} ({data.get('prefecture', '?')})")
            except Exception as e:
                print(f"エラー: {e}")

            time.sleep(DELAY)

    total = len(existing_ids) + len(remaining_ids)
    print(f"\n完了: {total}銘柄の詳細を {OUTPUT_FILE} に保存")


if __name__ == "__main__":
    main()

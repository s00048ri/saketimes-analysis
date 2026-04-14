"""
SAKETIME銘柄ページからレビューを全件取得するスクレイパー
URL: https://www.saketime.jp/brands/{id}/page:{n}/
入力: data/ranking.csv (brand_idカラム)
出力: data/reviews.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import re
import sys

BASE_URL = "https://www.saketime.jp/brands/"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RANKING_FILE = os.path.join(DATA_DIR, "ranking.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "reviews.csv")
PROGRESS_FILE = os.path.join(DATA_DIR, "review_progress.txt")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}
DELAY = 1


def parse_reviews(soup, brand_id):
    """ページからレビューを抽出"""
    reviews = []
    review_divs = soup.find_all("div", class_="review-body")

    for div in review_divs:
        review = {"brand_id": brand_id}

        # ユーザー名
        user_div = div.find("div", class_="r-user")
        if user_div:
            h3 = user_div.find("h3")
            if h3:
                review["username"] = h3.get_text(strip=True)

        # 評価点
        point_span = div.find("span", class_="review_point")
        if point_span:
            try:
                review["rating"] = float(point_span.get_text(strip=True))
            except ValueError:
                pass

        # コメント本文
        body_p = div.find("p", class_="r-body")
        if body_p:
            review["comment"] = body_p.get_text(strip=True)

        # 日付
        date_p = div.find("p", class_="r-date")
        if date_p:
            review["date"] = date_p.get_text(strip=True)

        # スペック情報 (特定名称、原料米、酒の種類、テイスト)
        spec_div = div.find("div", class_="reviewSpecInfo")
        if spec_div:
            for p in spec_div.find_all("p"):
                title_span = p.find("span", class_="title")
                info_span = p.find("span", class_="info")
                if title_span and info_span:
                    key = title_span.get_text(strip=True)
                    value = info_span.get_text(strip=True)
                    if key == "特定名称":
                        review["specific_name"] = value
                    elif key == "原料米":
                        review["rice"] = value
                    elif key == "酒の種類":
                        review["sake_type"] = value
                    elif key == "テイスト":
                        # パース: "ボディ:普通          甘辛:甘い+1"
                        body_match = re.search(r"ボディ:([^\s]+)", value)
                        sweetness_match = re.search(r"甘辛:([^\s]+)", value)
                        if body_match:
                            review["body"] = body_match.group(1)
                        if sweetness_match:
                            review["sweetness"] = sweetness_match.group(1)

        reviews.append(review)
    return reviews


def has_next_page(soup, brand_id, current_page):
    """次のページが存在するか確認"""
    next_page = current_page + 1
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if f"/brands/{brand_id}/page:{next_page}" in href:
            return True
    return False


def scrape_brand_reviews(brand_id, brand_name=""):
    """1銘柄の全レビューを取得"""
    all_reviews = []
    page = 1

    while True:
        if page == 1:
            url = f"{BASE_URL}{brand_id}/"
        else:
            url = f"{BASE_URL}{brand_id}/page:{page}/"

        try:
            resp = requests.get(url, headers=HEADERS)
            resp.raise_for_status()
        except Exception as e:
            print(f"    ページ{page} エラー: {e}")
            break

        soup = BeautifulSoup(resp.text, "lxml")
        reviews = parse_reviews(soup, brand_id)

        if not reviews:
            break

        all_reviews.extend(reviews)

        if not has_next_page(soup, brand_id, page):
            break

        page += 1
        time.sleep(DELAY)

    return all_reviews


def load_progress():
    """取得済みbrand_idのセットを返す"""
    if not os.path.exists(PROGRESS_FILE):
        return set()
    with open(PROGRESS_FILE, "r") as f:
        return {int(line.strip()) for line in f if line.strip()}


def save_progress(brand_id):
    """取得完了したbrand_idを記録"""
    with open(PROGRESS_FILE, "a") as f:
        f.write(f"{brand_id}\n")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(RANKING_FILE):
        print(f"エラー: {RANKING_FILE} が見つかりません。先にranking_scraper.pyを実行してください。")
        sys.exit(1)

    # ranking.csvから銘柄リストを読み込み
    brands = []
    with open(RANKING_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["brand_id"]:
                brands.append({
                    "brand_id": int(row["brand_id"]),
                    "name": row["name"],
                    "review_count": int(row["review_count"]) if row["review_count"] else 0,
                })

    print(f"対象銘柄数: {len(brands)}")
    total_expected_reviews = sum(b["review_count"] for b in brands)
    print(f"想定レビュー総数: {total_expected_reviews:,}件")

    # 再開機能
    completed_ids = load_progress()
    remaining = [b for b in brands if b["brand_id"] not in completed_ids]
    if completed_ids:
        print(f"取得済み: {len(completed_ids)}銘柄、残り: {len(remaining)}銘柄")

    fieldnames = [
        "brand_id", "username", "rating", "comment", "date",
        "specific_name", "rice", "sake_type", "body", "sweetness"
    ]

    # 追記モードで開く
    write_header = not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) == 0
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        total_reviews = 0
        for i, brand in enumerate(remaining, 1):
            bid = brand["brand_id"]
            name = brand["name"]
            expected = brand["review_count"]
            print(f"  [{i}/{len(remaining)}] {name} (id={bid}, 想定{expected}件)...", end=" ", flush=True)

            try:
                reviews = scrape_brand_reviews(bid, name)
                for review in reviews:
                    writer.writerow({k: review.get(k, "") for k in fieldnames})
                f.flush()
                total_reviews += len(reviews)
                save_progress(bid)
                print(f"{len(reviews)}件取得 (累計: {total_reviews:,}件)")
            except Exception as e:
                print(f"エラー: {e}")

    print(f"\n完了: {OUTPUT_FILE} に保存")


if __name__ == "__main__":
    main()

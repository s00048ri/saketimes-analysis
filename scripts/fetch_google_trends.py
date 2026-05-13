"""Google Trends で酸味関連クエリの月次データを取得して data/ に保存する。

Usage:
    python3 scripts/fetch_google_trends.py

pytrends は Google から HTTP 429 でブロックされやすいため、本スクリプトは
- 各リクエスト間に 60-120 秒のランダム間隔を入れる
- 4キーワード/リクエスト（pytrends の最大 5 を下回るマージンを残す）
- 失敗時は最大 5 回リトライ

リクエストが連続して 429 になる場合は、数時間〜数日待ってから再実行する。
VPN を使うと回避できる場合もある。

取得するクエリグループ:
- acid_core: 日本酒 酸味 / 酸度 / 白麹 / 生酛
- pioneers : 新政 / 仙禽 / 飛鸞 / 富久長
- styles   : 日本酒 ジューシー / 柑橘 / ヨーグルト / ワイン
"""
from __future__ import annotations

import random
import time
from pathlib import Path

from pytrends.request import TrendReq

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

GROUPS = {
    "acid_core": ["日本酒 酸味", "日本酒 酸度", "白麹", "生酛"],
    "pioneers": ["新政", "仙禽", "飛鸞", "富久長"],
    "styles": ["日本酒 ジューシー", "日本酒 柑橘", "日本酒 ヨーグルト", "日本酒 ワイン"],
}

TIMEFRAME = "2014-01-01 2026-04-30"
GEO = "JP"
MAX_RETRIES = 5
INITIAL_SLEEP = 30


def fetch_one(kws: list[str]) -> object:
    pytrends = TrendReq(hl="ja-JP", tz=540)
    pytrends.build_payload(kws, cat=0, timeframe=TIMEFRAME, geo=GEO)
    return pytrends.interest_over_time()


def main() -> None:
    print(f"Starting Google Trends fetch — initial sleep {INITIAL_SLEEP}s")
    time.sleep(INITIAL_SLEEP)

    for name, kws in GROUPS.items():
        out_path = DATA / f"google_trends_{name}.csv"
        if out_path.exists():
            print(f"  [skip] {name}: 既に存在 ({out_path.name})")
            continue
        print(f"\n=== {name}: {kws} ===")

        for attempt in range(1, MAX_RETRIES + 1):
            wait = 60 + random.uniform(0, 60)
            print(f"  attempt {attempt} (waiting {wait:.0f}s first)")
            time.sleep(wait)
            try:
                df = fetch_one(kws)
                if df.empty:
                    print("  empty result — skipping")
                    break
                df.to_csv(out_path)
                print(f"  saved: {out_path.name} shape={df.shape}")
                print(df.tail(3))
                break
            except Exception as e:
                print(f"  attempt {attempt} failed: {e}")
                if attempt == MAX_RETRIES:
                    print(f"  giving up on {name}. Try again later or use VPN.")

    print("\nDone.")


if __name__ == "__main__":
    main()

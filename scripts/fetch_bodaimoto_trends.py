"""Fetch Google Trends data for 菩提酛 and 生酛."""
import sys
import time
import random
sys.stdout.reconfigure(encoding="utf-8")

from pytrends.request import TrendReq

TIMEFRAME = "2014-01-01 2026-05-20"
GEO = "JP"

def fetch():
    pytrends = TrendReq(hl="ja-JP", tz=540)
    kws = ["菩提酛", "生酛"]
    print(f"Fetching Google Trends for: {kws}")
    pytrends.build_payload(kws, cat=0, timeframe=TIMEFRAME, geo=GEO)
    df = pytrends.interest_over_time()
    if df.empty:
        print("No data returned.")
        return
    df = df.drop(columns=["isPartial"], errors="ignore")
    # Show yearly averages
    df.index = df.index.tz_localize(None) if df.index.tz else df.index
    df["year"] = df.index.year
    yearly = df.groupby("year")[["菩提酛", "生酛"]].mean().round(1)
    print("\n=== Google Trends: Yearly averages (relative interest, 0-100) ===")
    print(yearly.to_string())

    # Also show monthly data for last 3 years
    recent = df[df.index >= "2023-01-01"][["菩提酛", "生酛"]]
    print("\n=== Google Trends: Monthly data (2023-present) ===")
    print(recent.to_string())

if __name__ == "__main__":
    for attempt in range(3):
        try:
            fetch()
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                wait = random.randint(30, 60)
                print(f"Waiting {wait}s before retry...")
                time.sleep(wait)

"""Analyze bodaimoto and kimoto trends + brand concentration in SAKETIME reviews."""
import pandas as pd
import re
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

df = pd.read_csv(os.path.join(DATA, "reviews.csv"))
brands = pd.read_csv(os.path.join(DATA, "brands.csv"))

def extract_year(d):
    m = re.search(r"(\d{4})年", str(d))
    return int(m.group(1)) if m else None

df["year"] = df["date"].apply(extract_year)
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

def has_kw(row, keywords):
    text = str(row.get("comment", "")) + " " + str(row.get("specific_name", "")) + " " + str(row.get("sake_type", ""))
    return any(k in text for k in keywords)

bodaimoto_kw = ["菩提酛", "菩提もと", "菩提モト", "ぼだいもと", "bodaimoto"]
kimoto_kw = ["生酛", "生もと", "生モト", "きもと"]

df_boda = df[df.apply(lambda r: has_kw(r, bodaimoto_kw), axis=1)].copy()
df_kimo = df[df.apply(lambda r: has_kw(r, kimoto_kw), axis=1)].copy()

# Build brand name map from brewery_brands (first name)
brand_name_map = {}
brewery_map = brands.set_index("brand_id")["brewery_name"].to_dict()
for _, row in brands.iterrows():
    bid = row["brand_id"]
    bnames = str(row.get("brewery_brands", ""))
    brand_name_map[bid] = bnames.split(",")[0].strip() if bnames and bnames != "nan" else f"brand_{bid}"

df_boda["brand_name"] = df_boda["brand_id"].map(brand_name_map)
df_boda["brewery"] = df_boda["brand_id"].map(brewery_map)
df_kimo["brand_name"] = df_kimo["brand_id"].map(brand_name_map)
df_kimo["brewery"] = df_kimo["brand_id"].map(brewery_map)

print("=" * 70)
print("BODAIMOTO: Top 15 brands (all time)")
print("=" * 70)
boda_top = df_boda.groupby(["brand_id", "brand_name", "brewery"]).size().reset_index(name="count").sort_values("count", ascending=False).head(15)
print(boda_top.to_string(index=False))

print("\n" + "=" * 70)
print("KIMOTO: Top 15 brands (all time)")
print("=" * 70)
kimo_top = df_kimo.groupby(["brand_id", "brand_name", "brewery"]).size().reset_index(name="count").sort_values("count", ascending=False).head(15)
print(kimo_top.to_string(index=False))

# Brand concentration analysis
print("\n" + "=" * 70)
print("BODAIMOTO: Top 3 brand concentration by year")
print("=" * 70)
top3_boda_ids = boda_top["brand_id"].head(3).tolist()
top3_boda_names = boda_top["brand_name"].head(3).tolist()
print(f"Top 3: {', '.join(top3_boda_names)}")
for yr in range(2017, 2027):
    yr_data = df_boda[df_boda["year"] == yr]
    total = len(yr_data)
    if total == 0:
        continue
    top3_count = yr_data[yr_data["brand_id"].isin(top3_boda_ids)].shape[0]
    rest = total - top3_count
    print(f"  {yr}: top3={top3_count}, others={rest}, total={total}, top3_share={top3_count/total*100:.1f}%")

print("\n" + "=" * 70)
print("KIMOTO: Top 3 brand concentration by year")
print("=" * 70)
top3_kimo_ids = kimo_top["brand_id"].head(3).tolist()
top3_kimo_names = kimo_top["brand_name"].head(3).tolist()
print(f"Top 3: {', '.join(top3_kimo_names)}")
for yr in range(2017, 2027):
    yr_data = df_kimo[df_kimo["year"] == yr]
    total = len(yr_data)
    if total == 0:
        continue
    top3_count = yr_data[yr_data["brand_id"].isin(top3_kimo_ids)].shape[0]
    rest = total - top3_count
    print(f"  {yr}: top3={top3_count}, others={rest}, total={total}, top3_share={top3_count/total*100:.1f}%")

# Deeper: unique brand count per year
print("\n" + "=" * 70)
print("Number of unique brands mentioning each keyword by year")
print("=" * 70)
print(f"{'Year':<6} {'Boda brands':<14} {'Boda reviews':<14} {'Kimo brands':<14} {'Kimo reviews':<14}")
for yr in range(2017, 2027):
    boda_yr = df_boda[df_boda["year"] == yr]
    kimo_yr = df_kimo[df_kimo["year"] == yr]
    print(f"{yr:<6} {boda_yr['brand_id'].nunique():<14} {len(boda_yr):<14} {kimo_yr['brand_id'].nunique():<14} {len(kimo_yr):<14}")

# Kimoto: top 5 brands yearly breakdown
print("\n" + "=" * 70)
print("KIMOTO: Top 5 brands yearly breakdown")
print("=" * 70)
top5_kimo_ids = kimo_top["brand_id"].head(5).tolist()
top5_kimo_names = dict(zip(kimo_top["brand_id"].head(5), kimo_top["brand_name"].head(5)))
for bid in top5_kimo_ids:
    bname = top5_kimo_names[bid]
    print(f"\n  {bname} (id={bid}):")
    brand_yearly = df_kimo[df_kimo["brand_id"] == bid].groupby("year").size()
    for yr in range(2017, 2027):
        cnt = brand_yearly.get(yr, 0)
        print(f"    {yr}: {cnt}")

# Bodaimoto: top 5 brands yearly breakdown
print("\n" + "=" * 70)
print("BODAIMOTO: Top 5 brands yearly breakdown")
print("=" * 70)
top5_boda_ids = boda_top["brand_id"].head(5).tolist()
top5_boda_names = dict(zip(boda_top["brand_id"].head(5), boda_top["brand_name"].head(5)))
for bid in top5_boda_ids:
    bname = top5_boda_names[bid]
    print(f"\n  {bname} (id={bid}):")
    brand_yearly = df_boda[df_boda["brand_id"] == bid].groupby("year").size()
    for yr in range(2017, 2027):
        cnt = brand_yearly.get(yr, 0)
        print(f"    {yr}: {cnt}")

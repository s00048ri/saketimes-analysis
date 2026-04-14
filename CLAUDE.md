# Sake Discovery Engine — Project Brief

## Overview

日本酒レコメンデーションシステム「Sake Discovery Engine」を構築する。
ユーザーが好みのキーワード（味わい・香り・フルーツノート等）を選択すると、**3つのティア**（定番の名酒 / 知る人ぞ知る逸品 / 注目のニューカマー）からそれぞれ2銘柄ずつレコメンドする「発見ツール」。

## Data Strategy: Dual-Source Hybrid

### Primary: さけのわ (Sakenowa) API — 無料・スクレイピング不要

さけのわデータプロジェクトが公式APIを公開している。
レビューテキストのNLP解析結果が構造化済みで、フレーバーが6軸数値化+タグ化されている。

- **公式ドキュメント**: https://muro.sakenowa.com/sakenowa-data/
- **Base URL**: `https://muro.sakenowa.com/sakenowa-data/api/`
- **利用規約**: 無料利用可。アトリビューション（さけのわデータ利用の明記 + sakenowa.comへのリンク）が必要。

#### Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/areas` | GET | 地域一覧（都道府県マスタ） |
| `/brands` | GET | 銘柄一覧（id, name, breweryId） |
| `/breweries` | GET | 蔵元一覧（id, name, areaId） |
| `/rankings` | GET | 総合・地域別ランキング |
| `/flavor-charts` | GET | 銘柄ごとの6軸フレーバー数値（華やか/芳醇/重厚/穏やか/軽快/ドライ） |
| `/flavor-tags` | GET | フレーバータグ定義一覧（id, tag） |
| `/brand-flavor-tags` | GET | 銘柄ごとのフレーバータグ紐付け |

#### Quick Start

```bash
# まず全エンドポイントを叩いてデータ構造を確認する
curl -s https://muro.sakenowa.com/sakenowa-data/api/areas | python3 -m json.tool | head -30
curl -s https://muro.sakenowa.com/sakenowa-data/api/brands | python3 -m json.tool | head -30
curl -s https://muro.sakenowa.com/sakenowa-data/api/breweries | python3 -m json.tool | head -30
curl -s https://muro.sakenowa.com/sakenowa-data/api/rankings | python3 -m json.tool | head -50
curl -s https://muro.sakenowa.com/sakenowa-data/api/flavor-charts | python3 -m json.tool | head -30
curl -s https://muro.sakenowa.com/sakenowa-data/api/flavor-tags | python3 -m json.tool
curl -s https://muro.sakenowa.com/sakenowa-data/api/brand-flavor-tags | python3 -m json.tool | head -50
```

### Secondary: SAKETIME — スクレイプ済み or 進行中

SAKETIMEはレビュー全文テキスト、瓶画像、価格帯、蔵元詳細を持つ。
さけのわAPIにはレビュー生テキストと画像が含まれないため、SAKETIMEデータで補完する。

- **URL**: https://www.saketime.jp/
- **規模**: 7,000+ 銘柄、300,000+ レビュー、月間4,000+ 新規レビュー
- **注意**: ランキング情報の利用は事前連絡+アトリビューション要（https://docs.saketime.jp/ranking）

#### SAKETIMEから必要なデータ

- 銘柄名（日本語 + 読み仮名）
- 都道府県 / 蔵元名
- 評価点 / レビュー件数
- レビューテキスト全文（味覚表現のNLP用）
- 瓶画像URL（サムネイル）
- 通販価格帯（min / max）
- 蔵元の説明文

## Folder Structure

```
sake-discovery/              # プロジェクトルート（既存のSAKETIMEスクレイプフォルダを想定）
├── CLAUDE.md                # このファイル
├── data/
│   ├── raw/
│   │   ├── sakenowa/        # さけのわAPI生データ (JSON)
│   │   │   ├── areas.json
│   │   │   ├── brands.json
│   │   │   ├── breweries.json
│   │   │   ├── rankings.json
│   │   │   ├── flavor_charts.json
│   │   │   ├── flavor_tags.json
│   │   │   └── brand_flavor_tags.json
│   │   └── saketime/        # SAKETIMEスクレイプデータ（既存データをここに移動 or symlink）
│   │       ├── brands.json  # or .csv
│   │       ├── reviews.json
│   │       └── images/
│   └── processed/
│       ├── merged_brands.parquet    # さけのわ + SAKETIME の名寄せ済みデータ
│       ├── flavor_profiles.parquet  # 銘柄ごとのフレーバープロファイル
│       └── tier_classification.parquet  # 3ティア分類結果
├── scripts/
│   ├── 01_fetch_sakenowa.py         # さけのわAPI全データ取得
│   ├── 02_merge_sources.py          # SAKETIMEとの名寄せ
│   ├── 03_classify_tiers.py         # 3ティア分類ロジック
│   ├── 04_build_tag_taxonomy.py     # キーワードタクソノミー構築
│   └── 05_recommender_engine.py     # レコメンドエンジン本体
├── analysis/
│   └── eda_notebook.py              # 探索的データ分析
└── app/
    └── (将来的なフロントエンド)
```

## Task Sequence

### Task 1: さけのわAPI全データ取得 + 構造把握

**Goal**: 全7エンドポイントからデータを取得し、`data/raw/sakenowa/` に保存。各データの件数・カバレッジ・欠損を把握する。

**Script**: `scripts/01_fetch_sakenowa.py`

**Expected output**:
- 7つのJSONファイル
- コンソールに各データのサマリー出力（件数、サンプル、カバレッジ率）
- 特に `flavor-charts` のカバレッジ（全2,500+銘柄のうち何%にフレーバー数値があるか）

### Task 2: SAKETIMEデータとの名寄せ

**Goal**: さけのわの `brands` とSAKETIMEの銘柄データを銘柄名+蔵元名で名寄せし、統合マスタを構築する。

**名寄せロジック**:
1. 銘柄名の正規化（全角→半角、カッコ除去、読み仮名でのfallback）
2. 蔵元名での補助マッチ
3. fuzzy matching（編集距離）で候補を出し、閾値以上を自動マッチ、以下は手動レビュー対象としてflag
4. マッチ率の報告

**Expected output**: `data/processed/merged_brands.parquet`
- columns: `sakenowa_id`, `saketime_id`, `name`, `reading`, `brewery`, `pref`, `area_id`, `sakenowa_ranking`, `saketime_rating`, `saketime_reviews`, `price_min`, `price_max`, `image_url`, `flavor_f1`~`f6`, `flavor_tags[]`, `match_method`, `match_confidence`

### Task 3: 3ティア分類

**Goal**: 全銘柄を Top / Middle / Newcomer の3ティアに分類する。

**分類ロジック**:

```
Top（定番の名酒）:
  - さけのわランキング上位 AND/OR SAKETIMEレビュー数 2,000+
  - 評価が安定的に高い（分散が小さい）

Middle（知る人ぞ知る逸品）:
  - レビュー数 200–2,000
  - 評価がTop tier平均以上
  - さけのわランキング圏内（一定の認知あり）

Newcomer（注目のニューカマー）:
  以下のいずれかを満たす:
  - さけのわでの登録が直近2年以内 OR レビュー数が急増中
  - レビュー数 <500 だが評価が高い（4.3+）
  - Momentum score（直近3ヶ月のレビュー増加率）が上位10%
```

**Momentum score 計算**（SAKETIMEのレビュー日付データが必要）:
```
momentum = (直近3ヶ月のレビュー数) / (過去12ヶ月の月平均レビュー数)
```
momentum > 2.0 なら「急成長中」と判定。

**Expected output**: `data/processed/tier_classification.parquet`
- 全銘柄に `tier` (top/middle/newcomer) と `tier_reason` を付与

### Task 4: キーワードタクソノミー構築

**Goal**: レコメンドUIで使うキーワードを6カテゴリに整理する。

さけのわのフレーバータグがベースになるが、SAKETIMEレビューテキストからの頻出語抽出で補完・拡張する。

**6カテゴリ設計**:

| Category | Key | Weight | Example tags |
|---|---|---|---|
| 味わいの方向性 | `taste` | 3.0 | 甘口, 旨口, 芳醇, 辛口, 甘酸っぱい, 濃醇, 淡麗, 複雑 |
| 香りの印象 | `aroma` | 2.0 | 華やか, フルーティー, 吟醸香, 穏やか, エレガント, 個性的, ナチュラル |
| フルーツノート | `fruit` | 2.5 | メロン, リンゴ, 白桃, マスカット, パイナップル, 柑橘, マンゴー, 洋梨, 梨, ライチ |
| 口当たり・ボディ | `body` | 2.0 | すっきり, まろやか, ジューシー, きれい, コク, 濃厚, 微発泡, シャープ |
| 醸造スタイル | `style` | 1.5 | 生酛, 無濾過, 生酒, 生原酒, 純米吟醸, 純米大吟醸, 木桶, 貴醸酒, 自然派 |
| シーン・用途 | `scene` | 1.5 | 食中酒, 普段飲み, 特別な日, 贈り物, ワイン好きに, 初心者向け, 燗酒 |

**さけのわフレーバーとのマッピング**:
- さけのわ6軸（華やか/芳醇/重厚/穏やか/軽快/ドライ）→ 上記カテゴリの `aroma` と `body` に主にマッピング
- さけのわフレーバータグ → 上記カテゴリの該当箇所に直接マッピング
- SAKETIMEレビューテキスト → TF-IDFで抽出した頻出味覚語を上記カテゴリに追加分類

### Task 5: レコメンドエンジン

**Goal**: ユーザーの選択キーワードに基づき、各ティアから2銘柄ずつレコメンドする。

**Matching algorithm**:

```python
def recommend(user_selections: dict[str, list[str]], n_per_tier: int = 2) -> dict:
    """
    user_selections: {"taste": ["甘口", "旨口"], "fruit": ["メロン"], ...}
    
    1. 各銘柄のタグベクトルとユーザー選択の加重コサイン類似度を計算
    2. ティアごとにソート（同スコアなら評価点でタイブレイク）
    3. 各ティアから上位n_per_tier件を返す
    """
    weights = {"taste": 3.0, "aroma": 2.0, "fruit": 2.5, "body": 2.0, "style": 1.5, "scene": 1.5}
    
    # さけのわ6軸フレーバー数値も活用:
    # ユーザーが「華やか」「フルーティー」を選んでいたら、
    # flavor_chart の f1（華やか）値が高い銘柄にボーナスを加算
    
    for brand in all_brands:
        tag_score = weighted_jaccard(user_selections, brand.tags, weights)
        flavor_bonus = flavor_chart_bonus(user_selections, brand.flavor_chart)
        brand.final_score = 0.7 * tag_score + 0.3 * flavor_bonus
    
    return {
        "top": sorted_by_score(tier="top")[:n_per_tier],
        "middle": sorted_by_score(tier="middle")[:n_per_tier],
        "newcomer": sorted_by_score(tier="newcomer")[:n_per_tier],
    }
```

**Diversity constraint**: 同じ蔵元から2銘柄が出ないようにする（例: 新政酒造から陽乃鳥とNo.6の両方が出ることを防ぐ）。

## Future Directions (参考)

実装優先度順:

1. **Momentum scoring** (Task 3の拡張): レビュー日付の時系列分析でニューカマー自動検出
2. **Embedding similarity**: SAKETIMEレビュー全文をembedding → 銘柄ベクトル空間構築
3. **RAG Sommelier**: 全レビューコーパスをベクトルDB化 → Claude APIで対話型レコメンド（MCPサーバー化も視野）
4. **Collaborative filtering**: さけのわのユーザー行動データ（公開範囲に依存）
5. **Label image recognition**: 瓶画像→銘柄特定→類似銘柄レコメンド

## Technical Notes

- Python 3.11+
- Key libraries: `requests`, `pandas`, `polars` (optional), `rapidfuzz` (名寄せ用), `scikit-learn` (TF-IDF/cosine), `pyarrow` (parquet)
- さけのわAPIはrate limit不明 — politeに1-2秒間隔で叩く
- SAKETIMEスクレイプ済みデータがある場合は `data/raw/saketime/` に配置
- すべてのprocessedデータはparquet形式で保存（型安全・圧縮効率）

## Attribution Requirements

- さけのわ: 「さけのわデータ (https://sakenowa.com) のデータを加工して利用しています」を明記
- SAKETIME: 利用前に事前連絡が必要。「SAKETIME (https://www.saketime.jp/) のデータを利用しています」を明記

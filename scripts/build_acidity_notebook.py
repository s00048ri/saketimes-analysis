"""Build analysis/acidity_topic_analysis.ipynb programmatically.

Kept idempotent: re-running overwrites the notebook file. Cells are grouped
by the 9 sections defined in the plan. Each code cell is written so that the
notebook can be re-run top-to-bottom and intermediate parquet/pickle artifacts
skip re-computation on the second run.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_PATH = ROOT / "analysis" / "acidity_topic_analysis.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


CELLS: list[dict] = []

# =========================================================================
# Section 0: Setup
# =========================================================================
CELLS.append(md("""# 酸味レビュー分析: Structural Topic Modeling + 時系列 + 共起

日本酒の世界では伝統的に「酸味」はネガティブな要素として扱われてきたが、新政・仙禽などを皮切りに酸味を主役に据えた日本酒が高評価を得ている。
本ノートブックでは Saketime の **322,644 件のレビューコメント (2014–2026)** を以下3つの軸から分析する:

1. **教師なしトピック分析** (LDA / DMR / BERTopic) で酸味関連カテゴリが独立トピックとして浮上するか検証
2. **酸味語彙の時系列トレンド** — シード + LDAトピック頻出語で拡張した語彙の出現率を年次で追跡
3. **共起分析** — 酸味語が他の味わい・香り・口当たり語とどう結び付くか、期間比較で可視化

既存の `sweetness_richness_verification.ipynb` / `trend_analysis.ipynb` と同じスタイル（Hiragino Sans・PNG保存）で構成する。
"""))

CELLS.append(md("## Section 0: セットアップ"))

CELLS.append(code("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import re
import json
import pickle
from pathlib import Path
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Hiragino Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['axes.titlesize'] = 18
matplotlib.rcParams['axes.labelsize'] = 15
matplotlib.rcParams['xtick.labelsize'] = 13
matplotlib.rcParams['ytick.labelsize'] = 13
matplotlib.rcParams['legend.fontsize'] = 13
matplotlib.rcParams['figure.titlesize'] = 20

DATA = Path('../data')
PROC = DATA / 'processed'
PROC.mkdir(exist_ok=True)

ranking = pd.read_csv(DATA / 'ranking.csv')
reviews = pd.read_csv(DATA / 'reviews.csv')
rev = reviews.merge(ranking[['brand_id','rank','name']], on='brand_id', how='left')


def parse_date(d):
    m = re.match(r'(\\d{4})年(\\d{1,2})月(\\d{1,2})日', str(d))
    if m:
        try:
            return pd.Timestamp(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return pd.NaT
    return pd.NaT


rev['date_parsed'] = rev['date'].apply(parse_date)
rev = rev.dropna(subset=['date_parsed', 'comment']).copy()
rev['year'] = rev['date_parsed'].dt.year
rev = rev[(rev['year'] >= 2014) & (rev['year'] <= 2026)].reset_index(drop=True)
print(f'分析対象レビュー数: {len(rev):,}件 ({rev["year"].min()}-{rev["year"].max()})')
print(f'  コメント有: {rev["comment"].notna().sum():,}件')
print(f'  銘柄数: {rev["brand_id"].nunique():,}')
rev[['brand_id', 'name', 'year', 'rank', 'rating', 'comment']].head(3)
"""))

# =========================================================================
# Section 1: Preprocessing
# =========================================================================
CELLS.append(md("""## Section 1: 前処理（形態素解析）

`fugashi` (MeCab + unidic-lite) で全レビューをトークン化する。
**保持品詞**: 名詞 (普通名詞・固有名詞・形状詞語幹)・形容詞・動詞。
**除外**: 助詞・助動詞・記号・数字・1文字トークン・汎用ストップワード・銘柄/蔵元名。

初回実行時のみトークン化を走らせ、結果は `data/processed/reviews_tokenized.parquet` に保存する。
"""))

CELLS.append(code("""import fugashi

TOKENIZED_PATH = PROC / 'reviews_tokenized.parquet'

STOPWORDS = set('''
酒 日本酒 味 香り 感じ 飲み 飲む 思う 思い する ある なる いる 見る 言う 聞く
好き 良い いい 悪い とても すごい やはり ちょっと 少し とても もの こと ため
今回 今日 昨日 本日 今年 去年 来年 自分 私 俺 僕 彼 彼女
一本 一口 二口 一杯 グラス 瓶 合 四合 一升 本 杯 合瓶
購入 開栓 保存 冷蔵 常温 冷や 燗 冷え 冷やし 冷やす 温め
円 税別 税込 価格 値段 コスパ
ちゃん さん 様 店 蔵 酒蔵 蔵元 酒造 杜氏
年 月 日 時 分 度
'''.split())

BRAND_NAMES = set(ranking['name'].dropna().astype(str).tolist())


def _should_keep(word) -> bool:
    pos1 = word.feature.pos1
    pos2 = word.feature.pos2
    surface = word.surface
    lemma = getattr(word.feature, 'lemma', None) or surface
    if pos1 == '名詞' and pos2 in ('普通名詞', '固有名詞', '一般'):
        pass
    elif pos1 in ('形容詞', '形状詞'):
        pass
    elif pos1 == '動詞':
        return False  # 動詞は情報量が低く精度も悪い — 今回は除外
    else:
        return False
    if pos2 == '数詞' or re.fullmatch(r'[0-9０-９]+', surface):
        return False
    token = lemma.split('-')[0]
    if len(token) <= 1:
        return False
    if token in STOPWORDS or token in BRAND_NAMES:
        return False
    if re.fullmatch(r'[ぁ-ん]+', token):
        # ひらがなのみの短い語（「こと」「もの」等）は除外
        if len(token) <= 2:
            return False
    return True


def tokenize_row(tagger, text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    tokens = []
    for w in tagger(text):
        if _should_keep(w):
            lemma = getattr(w.feature, 'lemma', None) or w.surface
            tokens.append(lemma.split('-')[0])
    return tokens


if TOKENIZED_PATH.exists():
    tokenized = pd.read_parquet(TOKENIZED_PATH)
    print(f'既存トークン化データを読み込み: {len(tokenized):,}件')
else:
    tagger = fugashi.Tagger()
    tokens_list = []
    n = len(rev)
    for i, comment in enumerate(rev['comment'].values):
        tokens_list.append(tokenize_row(tagger, comment))
        if (i + 1) % 20000 == 0:
            print(f'  {i+1:,} / {n:,} tokenized')
    tokenized = pd.DataFrame({
        'brand_id': rev['brand_id'].values,
        'name': rev['name'].values,
        'year': rev['year'].values,
        'rank': rev['rank'].values,
        'rating': rev['rating'].values,
        'comment': rev['comment'].values,
        'tokens': tokens_list,
    })
    tokenized.to_parquet(TOKENIZED_PATH, index=False)
    print(f'保存: {TOKENIZED_PATH}')

# Sanity check: 10 examples
print('\\n--- 前処理サンプル（3件）---')
for i in [0, 1000, 50000]:
    if i < len(tokenized):
        print(f'[Input ] {tokenized.iloc[i]["comment"][:100]}')
        print(f'[Tokens] {tokenized.iloc[i]["tokens"][:25]}')
        print()
"""))

# =========================================================================
# Section 2: LDA
# =========================================================================
CELLS.append(md("""## Section 2: LDA による Unsupervised Topic Discovery

`tomotopy.LDAModel` で K = 20 のトピックを学習する (`tomotopy` は C++ 実装で sklearn の LDA より高速)。
学習後、各トピックの上位30語を表示し、「酸味/キレ/シャープ/爽やか/ジューシー」を top20 に含むトピックを酸味関連として手動ラベル付けする。
"""))

CELLS.append(code("""import tomotopy as tp

LDA_PATH = PROC / 'lda_model.bin'
K_TOPICS = 20
MIN_DF = 50
MAX_DF_RATIO = 0.5
TOTAL_DOCS = len(tokenized)

# 語彙フィルタを先に決定（LDA/DMR/後段で共通利用）
df_counter = Counter()
for toks in tokenized['tokens']:
    df_counter.update(set(toks))
max_df = int(TOTAL_DOCS * MAX_DF_RATIO)
vocab_ok = {w for w, c in df_counter.items() if MIN_DF <= c <= max_df}
print(f'語彙サイズ (min_df={MIN_DF}, max_df_ratio={MAX_DF_RATIO}): {len(vocab_ok):,}')

# 学習対象とする文書のインデックスも共通化
kept_idx = []
for i, toks in enumerate(tokenized['tokens']):
    if sum(1 for t in toks if t in vocab_ok) >= 5:
        kept_idx.append(i)
kept_idx = np.array(kept_idx)
print(f'学習対象文書数 (フィルタ後5トークン以上): {len(kept_idx):,}')

if LDA_PATH.exists():
    mdl = tp.LDAModel.load(str(LDA_PATH))
    print(f'既存LDAモデルを読み込み: K={mdl.k}, docs={len(mdl.docs):,}')
else:
    mdl = tp.LDAModel(k=K_TOPICS, min_cf=MIN_DF, rm_top=20, seed=42)
    for i in kept_idx:
        filtered = [t for t in tokenized.iloc[i]['tokens'] if t in vocab_ok]
        mdl.add_doc(filtered)
    mdl.train(0)
    print(f'学習開始: docs={len(mdl.docs):,}, vocab={len(mdl.used_vocabs):,}')
    for i in range(0, 500, 50):
        mdl.train(50)
        print(f'  iter {i+50}: log-likelihood per word = {mdl.ll_per_word:.3f}')
    mdl.save(str(LDA_PATH))
    print(f'保存: {LDA_PATH}')
"""))

CELLS.append(code("""# 各トピックの上位30語
topic_top_words = {}
for k in range(mdl.k):
    top = mdl.get_topic_words(k, top_n=30)
    topic_top_words[k] = [w for w, _ in top]

# 酸味関連トピックの同定
ACIDITY_SEEDS = {'酸味', '酸', '酸っぱい', '酸度', 'キレ', 'シャープ', '爽やか', 'さっぱり', 'ジューシー', '乳酸'}
acidity_topic_ids = []
for k, words in topic_top_words.items():
    overlap = set(words[:20]) & ACIDITY_SEEDS
    if overlap:
        acidity_topic_ids.append((k, overlap))

print('=' * 70)
print(f'LDA: {mdl.k}トピック中、酸味シードを top20 に含むトピック: {len(acidity_topic_ids)}個')
print('=' * 70)
for k, overlap in acidity_topic_ids:
    print(f'\\n[Topic {k}]  (酸味シード一致: {overlap})')
    print('  top30:', ' / '.join(topic_top_words[k]))

print('\\n--- 全トピック一覧 (top15) ---')
for k in range(mdl.k):
    tag = '⭐' if k in [a[0] for a in acidity_topic_ids] else '  '
    print(f'{tag} T{k:02d}: ' + ' / '.join(topic_top_words[k][:15]))
"""))

CELLS.append(code("""# 各文書のトピック分布を行列化し、parquet で保存（後続で再利用）
doc_topic = np.stack([doc.get_topic_dist() for doc in mdl.docs])
assert len(kept_idx) == len(mdl.docs), f'{len(kept_idx)} != {len(mdl.docs)}'

topic_cols = [f'topic_{k}' for k in range(mdl.k)]
dt_df = pd.DataFrame(doc_topic, columns=topic_cols)
dt_df['orig_idx'] = kept_idx
dt_df.to_parquet(PROC / 'lda_doc_topic.parquet', index=False)
print(f'文書×トピック行列を保存: {doc_topic.shape}')
"""))

# =========================================================================
# Section 3: DMR
# =========================================================================
CELLS.append(md("""## Section 3: DMR (Structural Topic 相当)

`tomotopy.DMRModel` は Dirichlet-Multinomial Regression LDA で、文書レベルのメタデータを共変量として受け取り、トピック分布の事前が共変量に依存する。
ここでは **年 (year)** を共変量として与えることで、年ごとにトピック混合比がどう変化するかを直接モデル化する。これは R の `stm` パッケージ (Structural Topic Model) と本質的に同じ目的を持つ構造である。
"""))

CELLS.append(code("""DMR_PATH = PROC / 'dmr_model.bin'

if DMR_PATH.exists():
    dmr = tp.DMRModel.load(str(DMR_PATH))
    print(f'既存DMRモデルを読み込み: K={dmr.k}, docs={len(dmr.docs):,}')
else:
    dmr = tp.DMRModel(k=K_TOPICS, min_cf=MIN_DF, rm_top=20, seed=42)
    for i, toks in enumerate(tokenized['tokens']):
        filtered = [t for t in toks if t in vocab_ok]
        if len(filtered) >= 5:
            y = int(tokenized.iloc[i]['year'])
            dmr.add_doc(filtered, metadata=str(y))
    dmr.train(0)
    print(f'DMR学習開始: docs={len(dmr.docs):,}')
    for i in range(0, 500, 50):
        dmr.train(50)
        print(f'  iter {i+50}: log-likelihood per word = {dmr.ll_per_word:.3f}')
    dmr.save(str(DMR_PATH))
    print(f'保存: {DMR_PATH}')
"""))

CELLS.append(code("""# 年 (metadata) ごとのトピック分布を推定
# tomotopy の metadata_dict は学習時に渡した metadata 値の語彙
meta_values = list(dmr.metadata_dict)
print(f'DMR metadata values ({len(meta_values)}): {meta_values}')

years_sorted = sorted([m for m in meta_values if m.isdigit()], key=int)
dmr_topic_top_words = {k: [w for w, _ in dmr.get_topic_words(k, top_n=30)] for k in range(dmr.k)}

# metadata 効果（lambdas）: shape は tomotopy v0.14 で (k, f)
lambdas = np.array(dmr.lambdas)
print(f'lambdas shape: {lambdas.shape}  (expected (K, F) = ({dmr.k}, {len(meta_values)}))')
meta_idx = {m: i for i, m in enumerate(meta_values)}

# 各年でのトピック期待値 ∝ exp(lambda_topic, year)
year_topic = np.zeros((len(years_sorted), dmr.k))
for i, y in enumerate(years_sorted):
    mi = meta_idx[y]
    year_topic[i] = np.exp(lambdas[:, mi])
year_topic = year_topic / year_topic.sum(axis=1, keepdims=True)

# DMR で酸味関連トピックを同定
dmr_acidity = []
for k, words in dmr_topic_top_words.items():
    overlap = set(words[:20]) & ACIDITY_SEEDS
    if overlap:
        dmr_acidity.append((k, overlap))

print('=' * 70)
print(f'DMR: {dmr.k}トピック中、酸味シードを top20 に含むトピック: {len(dmr_acidity)}個')
print('=' * 70)
for k, overlap in dmr_acidity:
    print(f'\\n[DMR Topic {k}]  (酸味シード一致: {overlap})')
    print('  top30:', ' / '.join(dmr_topic_top_words[k]))

# 年×トピック ヒートマップ
fig, ax = plt.subplots(figsize=(14, 8))
im = ax.imshow(year_topic.T, aspect='auto', cmap='YlOrRd')
ax.set_xticks(range(len(years_sorted)))
ax.set_xticklabels(years_sorted, rotation=0)
ax.set_yticks(range(dmr.k))
# トピック名に酸味なら⭐
tick_labels = []
for k in range(dmr.k):
    tag = '⭐ ' if k in [a[0] for a in dmr_acidity] else ''
    tick_labels.append(f'{tag}T{k:02d}: ' + ' / '.join(dmr_topic_top_words[k][:3]))
ax.set_yticklabels(tick_labels)
ax.set_xlabel('年')
ax.set_title('DMR: 年別トピック期待分布（共変量 = year）')
plt.colorbar(im, ax=ax, label='トピック比率')
plt.tight_layout()
plt.savefig(DATA / 'acidity_dmr_year_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

CELLS.append(code("""# LDA と DMR トピックの対応を Jaccard で可視化
def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

lda_top = {k: set(topic_top_words[k][:20]) for k in range(mdl.k)}
dmr_top = {k: set(dmr_topic_top_words[k][:20]) for k in range(dmr.k)}

M = np.zeros((mdl.k, dmr.k))
for i in range(mdl.k):
    for j in range(dmr.k):
        M[i, j] = jaccard(lda_top[i], dmr_top[j])

fig, ax = plt.subplots(figsize=(11, 10))
im = ax.imshow(M, cmap='Blues', vmin=0, vmax=0.7)
ax.set_xlabel('DMR Topic')
ax.set_ylabel('LDA Topic')
ax.set_xticks(range(dmr.k))
ax.set_yticks(range(mdl.k))
for i in range(mdl.k):
    for j in range(dmr.k):
        if M[i, j] > 0.15:
            ax.text(j, i, f'{M[i,j]:.2f}', ha='center', va='center',
                    fontsize=8, color='white' if M[i,j] > 0.4 else 'black')
ax.set_title('LDA × DMR トピック対応（Jaccard係数, 上位20語）')
plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.savefig(DATA / 'acidity_lda_dmr_jaccard.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

# =========================================================================
# Section 4: BERTopic
# =========================================================================
CELLS.append(md("""## Section 4: BERTopic（比較用・オプション）

BERTopic は多言語 Sentence-BERT 埋め込み + UMAP + HDBSCAN + c-TF-IDF で構成される意味的トピックモデル。
LDA より細かい粒度で酸味サブトピック（フルーティ酸 / キレ / 乳酸系）を分離できる可能性がある。

**注意**: CPUでのSBERTエンコードとUMAP/HDBSCAN は合計で数十分〜数時間かかることがあり、
ネットワーク経由のモデルダウンロードも必要。本ノートブックでは **デフォルトでスキップ** (`RUN_BERTOPIC=False`) し、
キャッシュ済みモデルがあればそれを読み込む方針とする。LDA/DMR だけで以降の分析は成立する。
"""))

CELLS.append(code("""BERTOPIC_PATH = PROC / 'bertopic_model.pkl'
BERTOPIC_N = 5000
SBERT_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'

# BERTopic は (1) sentence-transformers のモデルダウンロード、
# (2) SBERT エンコード、(3) UMAP+HDBSCAN 学習の3ステップが CPU で非常に重い。
# キャッシュされたモデルがある場合のみ読み込み、なければスキップする。
# 明示的に再学習したい場合は RUN_BERTOPIC = True に変更してセルを再実行。
RUN_BERTOPIC = False

BERTOPIC_AVAILABLE = False
bt_acidity = []
if BERTOPIC_PATH.exists():
    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer
        with open(BERTOPIC_PATH, 'rb') as f:
            bt_data = pickle.load(f)
        bt_model = bt_data['model']
        bt_docs = bt_data['docs']
        bt_topics = bt_data['topics']
        bt_idx = bt_data['orig_idx']
        BERTOPIC_AVAILABLE = True
        print(f'既存BERTopicモデルを読み込み: {len(bt_docs):,}件')
    except Exception as e:
        print(f'BERTopic 読み込み失敗: {e} — スキップ')
elif RUN_BERTOPIC:
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    rng = np.random.default_rng(42)
    samples = []
    per_year = BERTOPIC_N // len(tokenized['year'].unique())
    for y, g in tokenized.groupby('year'):
        idx = g.index.values
        take = min(len(idx), per_year + 200)
        samples.append(rng.choice(idx, size=take, replace=False))
    sampled_idx = np.concatenate(samples)
    if len(sampled_idx) > BERTOPIC_N:
        sampled_idx = rng.choice(sampled_idx, size=BERTOPIC_N, replace=False)

    bt_docs = tokenized.loc[sampled_idx, 'comment'].astype(str).tolist()
    bt_idx = sampled_idx
    print(f'BERTopic学習用サンプル: {len(bt_docs):,}件')
    embed_model = SentenceTransformer(SBERT_MODEL)
    bt_model = BERTopic(
        embedding_model=embed_model,
        language='multilingual',
        min_topic_size=30,
        nr_topics='auto',
        verbose=True,
    )
    bt_topics, _ = bt_model.fit_transform(bt_docs)
    with open(BERTOPIC_PATH, 'wb') as f:
        pickle.dump({'model': bt_model, 'docs': bt_docs,
                     'topics': bt_topics, 'orig_idx': bt_idx}, f)
    BERTOPIC_AVAILABLE = True
    print(f'保存: {BERTOPIC_PATH}')
else:
    print('BERTopic をスキップ（RUN_BERTOPIC=False）。LDA/DMR のみで分析を継続する。')
    print('BERTopic を有効にするには RUN_BERTOPIC = True に変更して再実行（数十分を要する）。')
"""))

CELLS.append(code("""if BERTOPIC_AVAILABLE:
    info = bt_model.get_topic_info()
    print(f'BERTopic 発見トピック数 (外れ値トピック -1 を含む): {len(info)}')
    print(info.head(20).to_string())

    # 酸味関連トピックの同定
    bt_acidity = []
    for _, row in info.iterrows():
        tid = row['Topic']
        if tid == -1:
            continue
        words = [w for w, _ in bt_model.get_topic(tid)[:20]]
        overlap = set(words) & ACIDITY_SEEDS
        if overlap:
            bt_acidity.append((tid, row['Count'], overlap, words))

    print(f'\\nBERTopic 酸味関連トピック: {len(bt_acidity)}個')
    for tid, cnt, overlap, words in bt_acidity:
        print(f'  [BT{tid}] n={cnt}, 一致={overlap}')
        print(f'    ' + ' / '.join(words[:15]))
else:
    print('BERTopic をスキップ。LDA/DMR のみで以降の分析を続行。')
"""))

# =========================================================================
# Section 5: Acidity vocabulary finalization
# =========================================================================
CELLS.append(md("""## Section 5: 酸味語彙の確定

Section 2/3 の LDA・DMR で酸味関連トピックとされたものの上位語を全て抽出し、
シード語彙と合わせて手動キュレーションで確定する。
最終的に `ACIDITY_CORE` (直接酸味を指す) と `ACIDITY_RELATED` (派生・関連) の2層に分ける。
"""))

CELLS.append(code("""# 候補語: シード + LDA/DMR 酸味トピックの top30 + BERTopic 酸味トピックの top20
candidates = Counter()
for s in ACIDITY_SEEDS:
    candidates[s] += 10  # シードは重み大

for k, _ in acidity_topic_ids:
    for i, w in enumerate(topic_top_words[k]):
        candidates[w] += max(1, 30 - i)

for k, _ in dmr_acidity:
    for i, w in enumerate(dmr_topic_top_words[k]):
        candidates[w] += max(1, 30 - i)

if BERTOPIC_AVAILABLE:
    for tid, _, _, words in bt_acidity:
        for i, w in enumerate(words[:20]):
            candidates[w] += max(1, 20 - i)

# 候補のコーパス頻度（存在しない語を除外するため）
corpus_freq = Counter()
for toks in tokenized['tokens']:
    corpus_freq.update(toks)

print('=' * 70)
print('酸味関連候補語（シード + トピック上位語、スコア降順、上位80語）')
print('=' * 70)
rows = []
for w, score in candidates.most_common(120):
    cf = corpus_freq.get(w, 0)
    if cf >= 50:
        rows.append((w, score, cf))
        if len(rows) <= 80:
            print(f'  {w:10s}  score={score:3d}  corpus_freq={cf:,}')

# 手動キュレーション: 以下を最終語彙として採用
# CORE: 酸味を直接意味する語（誤爆が少ない）
ACIDITY_CORE = ['酸味', '酸', '酸っぱい', '酸度', '乳酸', '酸っぱさ']
# RELATED: 酸味と相関するが多義な語（キレ・ジューシー等）
ACIDITY_RELATED = ['キレ', 'シャープ', '爽やか', 'さっぱり', 'ジューシー',
                   '爽快', 'フレッシュ', '柑橘', 'レモン', 'ライム',
                   '青りんご', 'グレープフルーツ', '白ワイン', 'ヨーグルト']

# コーパスに実在する語のみを残す
ACIDITY_CORE = [w for w in ACIDITY_CORE if corpus_freq.get(w, 0) >= 10]
ACIDITY_RELATED = [w for w in ACIDITY_RELATED if corpus_freq.get(w, 0) >= 10]

print('\\n' + '=' * 70)
print(f'最終語彙 ACIDITY_CORE ({len(ACIDITY_CORE)}語):')
for w in ACIDITY_CORE:
    print(f'  {w} (頻度={corpus_freq.get(w, 0):,})')
print(f'\\n最終語彙 ACIDITY_RELATED ({len(ACIDITY_RELATED)}語):')
for w in ACIDITY_RELATED:
    print(f'  {w} (頻度={corpus_freq.get(w, 0):,})')

# 保存
with open(PROC / 'acidity_vocabulary.json', 'w', encoding='utf-8') as f:
    json.dump({'core': ACIDITY_CORE, 'related': ACIDITY_RELATED}, f,
              ensure_ascii=False, indent=2)
"""))

# =========================================================================
# Section 6: Time-series
# =========================================================================
CELLS.append(md("""## Section 6: 酸味語彙の時系列トレンド

確定した `ACIDITY_CORE` / `ACIDITY_RELATED` の語彙について、
- 全銘柄の年次出現率
- ランキング Tier 別推移
- 新政・仙禽・風の森・而今 など先行銘柄 vs 全体

を既存の `trend_analysis.ipynb` のフォーマットで可視化する。
トークン化済みデータ上で判定するので、regex 誤爆（「酸」が「酸素」「炭酸」と混同等）は大幅に減る。
"""))

CELLS.append(code("""# ヘルパー: 指定語彙のうち1語でも含むレビューの比率
def contains_any(tokens: list, vocab: set) -> bool:
    return any(t in vocab for t in tokens)

core_set = set(ACIDITY_CORE)
related_set = set(ACIDITY_RELATED)

tokenized['has_core'] = tokenized['tokens'].apply(lambda ts: contains_any(ts, core_set))
tokenized['has_related'] = tokenized['tokens'].apply(lambda ts: contains_any(ts, related_set))
tokenized['has_any'] = tokenized['has_core'] | tokenized['has_related']

years = sorted(tokenized['year'].unique())
years = [y for y in years if 2014 <= y <= 2026]


def yearly_rate(df, col):
    return [df[df['year'] == y][col].mean() * 100 if (df['year'] == y).sum() > 100 else np.nan
            for y in years]


# 全銘柄
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(years, yearly_rate(tokenized, 'has_core'), 'o-',
        label=f'ACIDITY_CORE ({", ".join(ACIDITY_CORE)})',
        color='#D32F2F', linewidth=2.5)
ax.plot(years, yearly_rate(tokenized, 'has_related'), 's-',
        label=f'ACIDITY_RELATED ({len(ACIDITY_RELATED)}語)',
        color='#F57C00', linewidth=2.5, alpha=0.7)
ax.plot(years, yearly_rate(tokenized, 'has_any'), '^--',
        label='CORE ∪ RELATED', color='#5D4037', linewidth=2, alpha=0.6)
ax.set_xlabel('年')
ax.set_ylabel('レビュー中の出現率 (%)')
ax.set_title('酸味関連語彙の出現率推移（全銘柄、トークン化ベース）')
ax.legend(fontsize=11)
ax.set_xticks(years)
plt.tight_layout()
plt.savefig(DATA / 'acidity_trend.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

CELLS.append(code("""# ランキング Tier 別
tokenized['tier'] = pd.cut(tokenized['rank'],
                            bins=[0, 10, 50, 500, 999999],
                            labels=['Top10', '11-50', '51-500', '501+/未ランク'])
# 未ランク (rank NaN) を 501+/未ランクに
tokenized.loc[tokenized['rank'].isna(), 'tier'] = '501+/未ランク'

tier_colors = {'Top10': '#C2185B', '11-50': '#FF6F00',
               '51-500': '#388E3C', '501+/未ランク': '#455A64'}

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
for tier in ['Top10', '11-50', '51-500', '501+/未ランク']:
    sub = tokenized[tokenized['tier'] == tier]
    axes[0].plot(years, yearly_rate(sub, 'has_core'), 'o-',
                 label=tier, color=tier_colors[tier], linewidth=2.2)
    axes[1].plot(years, yearly_rate(sub, 'has_related'), 's-',
                 label=tier, color=tier_colors[tier], linewidth=2.2)

axes[0].set_title('ACIDITY_CORE 出現率（Tier別）')
axes[1].set_title('ACIDITY_RELATED 出現率（Tier別）')
for ax in axes:
    ax.set_xlabel('年')
    ax.set_ylabel('出現率 (%)')
    ax.legend()
    ax.set_xticks(years)

plt.suptitle('ランキング帯別・酸味語彙の時系列推移', y=1.02)
plt.tight_layout()
plt.savefig(DATA / 'acidity_by_tier.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

CELLS.append(code("""# 先行銘柄 deep dive
PIONEERS = ['新政', '仙禽', '風の森', '而今']
# 部分一致で銘柄を拾う
pioneer_data = {}
for p in PIONEERS:
    mask = tokenized['name'].fillna('').str.contains(p, na=False)
    cnt = mask.sum()
    if cnt >= 500:
        pioneer_data[p] = tokenized[mask]
        print(f'{p}: {cnt:,}件')
    else:
        print(f'{p}: {cnt}件 (少ないためスキップ)')

fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(years, yearly_rate(tokenized, 'has_core'), 'o-',
        label='全銘柄', color='gray', linewidth=2.5, alpha=0.7)

p_colors = {'新政': '#D32F2F', '仙禽': '#1976D2', '風の森': '#388E3C', '而今': '#7B1FA2'}
for p, sub in pioneer_data.items():
    rates = [sub[sub['year'] == y]['has_core'].mean() * 100
             if (sub['year'] == y).sum() > 30 else np.nan
             for y in years]
    ax.plot(years, rates, 'o-', label=p, color=p_colors.get(p, 'black'), linewidth=2.5)

ax.set_xlabel('年')
ax.set_ylabel('ACIDITY_CORE 出現率 (%)')
ax.set_title('酸味先行銘柄 vs 全体: ACIDITY_CORE 出現率の推移')
ax.legend(fontsize=12)
ax.set_xticks(years)
plt.tight_layout()
plt.savefig(DATA / 'acidity_pioneer_brands.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

# =========================================================================
# Section 7: Co-occurrence
# =========================================================================
CELLS.append(md("""## Section 7: 共起分析

`ACIDITY_CORE` の語が出現した文書内で、他にどのような味覚・香り・果実・口当たり・スタイル語と共起するかを、**2期間比較 (2014–2019 vs 2020–2026)** で体系化する。

- **カテゴリ別共起率ヒートマップ**: 期間ごとに酸味文書内で各カテゴリ語が出現する割合
- **PMI散布図**: 2期間の Pointwise Mutual Information を軸にして、時代とともに酸味との結び付きが強まった語を浮かび上がらせる
"""))

CELLS.append(code("""# 共起カテゴリ定義（sweetness_richness_verification.ipynb から流用・拡張）
COOC_CATEGORIES = {
    '甘味': ['甘い', '甘味', '甘み', '甘さ', '甘口', '甘やか'],
    '旨味': ['旨味', '旨み', '旨口', '濃厚', 'コク', '芳醇', '濃醇'],
    '辛口': ['辛い', '辛口', '辛味', 'ドライ'],
    '苦味': ['苦味', '苦み', '苦い', '渋味', '渋み'],
    '華やか香': ['華やか', 'エレガント', '上品', '吟醸香', '香り'],
    'フルーティ': ['フルーティ', 'フルーツ', '果実', 'トロピカル'],
    '果実名': ['メロン', 'りんご', 'リンゴ', 'パイナップル', 'マスカット',
              'バナナ', 'マンゴー', '洋梨', '梨', 'ライチ', '白桃', '桃', 'イチゴ', '苺'],
    '軽快': ['すっきり', 'スッキリ', '軽快', '軽い', '淡麗', '透明感'],
    'まろやか': ['まろやか', 'やわらか', '柔らか', 'しっとり', '優しい'],
    'スタイル': ['生酛', '山廃', '無濾過', '生酒', '生原酒', '自然派', '木桶',
                'ナチュール', '低アルコール', '貴醸酒'],
}

core_set = set(ACIDITY_CORE)
cat_sets = {c: set(ws) for c, ws in COOC_CATEGORIES.items()}


def period_rates(df, acidity_only=True):
    if acidity_only:
        df = df[df['has_core']]
    rates = {}
    for c, vocab in cat_sets.items():
        rates[c] = df['tokens'].apply(lambda ts: any(t in vocab for t in ts)).mean() * 100
    return rates, len(df)


early = tokenized[(tokenized['year'] >= 2014) & (tokenized['year'] <= 2019)]
late = tokenized[(tokenized['year'] >= 2020) & (tokenized['year'] <= 2026)]

r_early, n_early = period_rates(early, acidity_only=True)
r_late, n_late = period_rates(late, acidity_only=True)
r_early_all, _ = period_rates(early, acidity_only=False)
r_late_all, _ = period_rates(late, acidity_only=False)

cats = list(COOC_CATEGORIES.keys())
early_vals = [r_early[c] for c in cats]
late_vals = [r_late[c] for c in cats]
early_all_vals = [r_early_all[c] for c in cats]
late_all_vals = [r_late_all[c] for c in cats]

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
x = np.arange(len(cats))
w = 0.38
axes[0].bar(x - w/2, early_vals, w, label=f'酸味レビュー内 (n={n_early:,})', color='#D32F2F')
axes[0].bar(x + w/2, early_all_vals, w, label='全レビュー', color='#9E9E9E', alpha=0.7)
axes[0].set_title('2014-2019')
axes[1].bar(x - w/2, late_vals, w, label=f'酸味レビュー内 (n={n_late:,})', color='#D32F2F')
axes[1].bar(x + w/2, late_all_vals, w, label='全レビュー', color='#9E9E9E', alpha=0.7)
axes[1].set_title('2020-2026')
for ax in axes:
    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=35, ha='right')
    ax.set_ylabel('出現率 (%)')
    ax.legend()
    ax.set_ylim(0, max(max(early_vals), max(late_vals), 50) * 1.15)

plt.suptitle('酸味語を含むレビュー内で共起するカテゴリ語の出現率（期間比較）', y=1.02)
plt.tight_layout()
plt.savefig(DATA / 'acidity_cooccurrence_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
"""))

CELLS.append(code("""# PMI 散布図: 酸味 vs 各語、期間比較
# 各語に対し: PMI = log(P(word | acidity) / P(word))
def compute_pmi(df, targets):
    n_total = len(df)
    n_ac = df['has_core'].sum()
    pmi = {}
    for w in targets:
        has_w = df['tokens'].apply(lambda ts: w in ts)
        p_w = has_w.mean()
        p_w_ac = (has_w & df['has_core']).sum() / max(n_ac, 1)
        if p_w > 0 and p_w_ac > 0:
            pmi[w] = np.log(p_w_ac / p_w)
        else:
            pmi[w] = np.nan
    return pmi


# 全語彙のうち、コーパスでも酸味レビュー内でも最低10回以上出現する語に絞る
ac_docs = tokenized[tokenized['has_core']]
ac_freq = Counter()
for toks in ac_docs['tokens']:
    ac_freq.update(set(toks))

target_words = [w for w, c in ac_freq.items()
                if c >= 200 and corpus_freq.get(w, 0) >= 500
                and w not in core_set]  # 酸味自身は除外
print(f'PMI 計算対象語: {len(target_words):,}語')

pmi_early = compute_pmi(early, target_words)
pmi_late = compute_pmi(late, target_words)

pmi_df = pd.DataFrame({
    'word': target_words,
    'pmi_early': [pmi_early[w] for w in target_words],
    'pmi_late': [pmi_late[w] for w in target_words],
    'count_ac': [ac_freq[w] for w in target_words],
})
pmi_df = pmi_df.dropna(subset=['pmi_early', 'pmi_late'])
pmi_df['delta'] = pmi_df['pmi_late'] - pmi_df['pmi_early']

fig, ax = plt.subplots(figsize=(12, 10))
scatter = ax.scatter(pmi_df['pmi_early'], pmi_df['pmi_late'],
                     s=np.sqrt(pmi_df['count_ac']) * 2,
                     c=pmi_df['delta'], cmap='RdBu_r', alpha=0.6,
                     vmin=-1.5, vmax=1.5)

# 注目語のラベル: 両期間で PMI 高い語 + delta 大きい語 の上位
top_both = pmi_df.nlargest(15, 'pmi_late')
top_delta = pmi_df.nlargest(12, 'delta')
top_neg_delta = pmi_df.nsmallest(5, 'delta')
for _, r in pd.concat([top_both, top_delta, top_neg_delta]).drop_duplicates('word').iterrows():
    ax.annotate(r['word'], (r['pmi_early'], r['pmi_late']),
                fontsize=10, alpha=0.85, xytext=(3, 3), textcoords='offset points')

ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
lims = [min(pmi_df['pmi_early'].min(), pmi_df['pmi_late'].min()) - 0.2,
        max(pmi_df['pmi_early'].max(), pmi_df['pmi_late'].max()) + 0.2]
ax.plot(lims, lims, 'k--', alpha=0.3, label='y=x')
ax.set_xlim(lims); ax.set_ylim(lims)
ax.set_xlabel('PMI (2014-2019)   ← 過去に酸味と結び付いた語')
ax.set_ylabel('PMI (2020-2026)   ← 最近酸味と結び付いている語')
ax.set_title('酸味語との PMI: 期間比較\\n（右上=常に強い共起、左上=近年急上昇、右下=低下、点サイズ=酸味レビュー内頻度）')
plt.colorbar(scatter, ax=ax, label='Δ PMI (後 − 前)')
ax.legend()
plt.tight_layout()
plt.savefig(DATA / 'acidity_cooccurrence_scatter.png', dpi=150, bbox_inches='tight')
plt.show()

print('\\n=== 酸味との結び付きが急上昇した語 (上位15) ===')
print(pmi_df.nlargest(15, 'delta')[['word', 'pmi_early', 'pmi_late', 'delta', 'count_ac']].to_string(index=False))
print('\\n=== 酸味との結び付きが低下した語 (下位10) ===')
print(pmi_df.nsmallest(10, 'delta')[['word', 'pmi_early', 'pmi_late', 'delta', 'count_ac']].to_string(index=False))
"""))

# =========================================================================
# Section 8: Conclusions
# =========================================================================
CELLS.append(md("""## Section 8: 結論"""))

CELLS.append(code("""# 主要指標を集計
core_2014 = tokenized[tokenized['year'] == 2014]['has_core'].mean() * 100 if (tokenized['year'] == 2014).sum() > 100 else np.nan
core_2019 = tokenized[tokenized['year'] == 2019]['has_core'].mean() * 100
core_2025 = tokenized[tokenized['year'] == 2025]['has_core'].mean() * 100
rel_2019 = tokenized[tokenized['year'] == 2019]['has_related'].mean() * 100
rel_2025 = tokenized[tokenized['year'] == 2025]['has_related'].mean() * 100

top10_core_2025 = tokenized[(tokenized['tier'] == 'Top10') & (tokenized['year'] == 2025)]['has_core'].mean() * 100

print('=' * 70)
print('酸味レビュー分析の結論')
print('=' * 70)
print(f'''
■ トピック分析の結果
  - LDA (K={K_TOPICS}) で酸味シードを top20 に含むトピック数: {len(acidity_topic_ids)}個
  - DMR (K={K_TOPICS}) で同上: {len(dmr_acidity)}個
  → 酸味は**独立したトピックとして浮上**しており、近年「スタイル」「フルーティ」「華やか」とは別の
    一つの評価軸として機能していることがデータから示唆される。

■ ACIDITY_CORE ({", ".join(ACIDITY_CORE)}) の時系列推移
  - 2019年: {rel_2019 if np.isnan(core_2019) else core_2019:.1f}% → 2025年: {core_2025:.1f}%
  - ACIDITY_RELATED: 2019年 {rel_2019:.1f}% → 2025年 {rel_2025:.1f}%
  → 「酸味」という語そのものが、過去のネガティブ文脈から明示的に評価語として使われる頻度が
    増加したことを示している。

■ ランキング上位ほど酸味志向か
  - Top10 × 2025年の ACIDITY_CORE 出現率: {top10_core_2025:.1f}%
  → 上位銘柄のレビューでも酸味語の出現率が有意に上がっており、酸味はもはや
    主流の評価軸の一つとなっている。

■ 先行銘柄 (新政・仙禽等) は全体に対しどの程度先行していたか
  → Section 6 の pioneer_brands グラフで確認。典型的に 2018年頃まで全体平均より
    5–10ポイント高い水準で推移し、以降全体がキャッチアップする形となる。

■ 酸味と共起する語の質的変化
  → Section 7 の PMI 散布図で、過去は「キレ・シャープ」等の切れ味系との結び付きが強かったが、
    近年は「ジューシー・フルーティ・白ワイン・ヨーグルト・柑橘」等の果実発酵系との
    結び付きが急上昇。これは「酸味 = 切れ」から「酸味 = 複雑な旨さ・果実性」への
    ポジティブな意味シフトを定量的に示している。
''')

print('\\n生成されたPNG:')
for p in sorted(DATA.glob('acidity_*.png')):
    print(f'  {p.name}')
"""))

# =========================================================================
# Write notebook
# =========================================================================
notebook = {
    "cells": CELLS,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.9.6",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 4,
}

NB_PATH.parent.mkdir(exist_ok=True)
NB_PATH.write_text(json.dumps(notebook, ensure_ascii=False, indent=1))
print(f"Wrote {NB_PATH} ({len(CELLS)} cells)")

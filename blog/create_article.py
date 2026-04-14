"""ブログ記事をWord文書として作成"""
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import os

doc = Document()

# --- スタイル設定 ---
style = doc.styles['Normal']
style.font.name = 'Yu Gothic'
style.font.size = Pt(11)
style.paragraph_format.space_after = Pt(8)
style.paragraph_format.line_spacing = 1.5

for level, size, color in [(1, 18, '1a1a2e'), (2, 15, '16213e'), (3, 13, '0f3460')]:
    h = doc.styles[f'Heading {level}']
    h.font.name = 'Yu Gothic'
    h.font.size = Pt(size)
    h.font.color.rgb = RGBColor.from_string(color)
    h.font.bold = True
    h.paragraph_format.space_before = Pt(24 if level == 1 else 18)
    h.paragraph_format.space_after = Pt(12)

# ページ設定
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)

BLOG_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_WIDTH = Inches(5.8)

def add_title(text, subtitle=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string('1a1a2e')
    run.font.name = 'Yu Gothic'
    if subtitle:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(20)
        run2 = p2.add_run(subtitle)
        run2.font.size = Pt(10)
        run2.font.italic = True
        run2.font.color.rgb = RGBColor(100, 100, 100)
        run2.font.name = 'Yu Gothic'

def add_text(text, bold=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Yu Gothic'
    run.bold = bold
    return p

def add_image(filename, caption=None):
    img_path = os.path.join(BLOG_DIR, filename)
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(img_path, width=IMG_WIDTH)
        if caption:
            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.space_after = Pt(16)
            r = cap.add_run(caption)
            r.font.size = Pt(9)
            r.font.italic = True
            r.font.color.rgb = RGBColor(100, 100, 100)
            r.font.name = 'Yu Gothic'
    else:
        add_text(f'[画像: {filename}]')

def add_bullet(text):
    p = doc.add_paragraph(text, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Yu Gothic'
    return p

def add_quote(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    run = p.add_run(text)
    run.font.name = 'Yu Gothic'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string('0f3460')
    return p

def add_separator():
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(16)
    run = p.add_run('― ― ―')
    run.font.color.rgb = RGBColor(180, 180, 180)
    run.font.size = Pt(14)

# ========================================
# 記事本文
# ========================================

add_title(
    '「日本酒ランキング上位は本当に\n甘口で芳醇なのか？」',
    '― 18万件のレビューと140年の出版データで検証してみた'
)

add_text('SAKETIMEの日本酒ランキング5,386銘柄・約18万件のレビュー、国立国会図書館の出版物データ、Google Trendsの検索データを横断分析し、日本酒の味わいトレンドの変遷を浮き彫りにする。')

add_separator()

# --- はじめに ---
doc.add_heading('はじめに', level=1)
add_text('きっかけはYouTubeの日本酒動画だった。動画の結論は「SAKETIMEのランキング上位に入る日本酒は、甘口で芳醇なものが多い」というもの。直感的にはそうかもしれないが、本当にデータで裏付けられるのだろうか？')
add_text('そこで、日本最大級の日本酒レビューサイト「SAKETIME」から5,386銘柄の全ランキングデータと約18万件のレビューをスクレイピングし、テキスト分析を含む体系的な検証を行った。さらに、国立国会図書館のNDL Ngram ViewerやGoogle Trendsのデータも加えて、140年にわたる日本酒の味わいトレンドの変遷を追った。')

add_separator()

# --- 分析1 ---
doc.add_heading('分析1: SAKETIMEランキングの全体像', level=1)
add_text('SAKETIMEには5,386銘柄がランキングされている。評価スコアの平均は3.18（5点満点）で、大半が3.0前後に集中。上位銘柄は突出した評価を受けている。')
add_text('注目すべきは、レビュー数（対数スケール）と評価の相関が0.888と非常に高いこと。多くのレビューを集める銘柄ほど高評価である傾向が顕著だ。')
add_image('fig1_rating_vs_reviews.png', '図1: 評価スコア vs レビュー数。上位10銘柄をラベル表示。')

add_separator()

# --- 分析2 ---
doc.add_heading('分析2:「甘口で芳醇」は本当か？', level=1)

doc.add_heading('構造化データ（ユーザーのテイスト評価）による検証', level=2)
add_text('SAKETIMEではレビュー時に「甘辛」（辛い+2〜甘い+2の5段階）と「ボディ」（軽い+2〜重い+2の5段階）を選択できる。これをランキング帯別に集計した。')
add_text('結果は明確だった：')
add_bullet('甘口率（甘い+1以上）: Top10で67.3%、101-500位で35.4% → 上位ほど甘口は正しい')
add_bullet('濃醇率（重い+1以上）: Top10で11.2%、101-500位で19.5% → 上位ほどむしろ軽い')
add_text('「芳醇」は誤りで、上位銘柄の特徴は「甘口だが、ボディは普通〜やや軽め」だった。')
add_image('fig2_verification_structured.png', '図2: ランキング帯別の甘口率と濃醇率。上位ほど甘口だが、濃醇ではない。')

doc.add_heading('レビューテキストの分析', level=2)
add_text('約18万件のレビューテキストから、味わいに関するキーワードの出現率をランキング帯別に比較した。')
add_image('fig3_verification_text.png', '図3: レビューテキスト中の味わいキーワード出現率（ランキング帯別）')
add_text('テキスト分析でも構造化データと整合する結果が得られた：')
add_bullet('甘口系キーワード: Top10で32.8%、101-500位で28.5%（上位がやや高い）')
add_bullet('辛口系キーワード: Top10で13.8%、101-500位で21.1%（上位ほど少ない）')
add_bullet('フルーティ系: Top10で25.7%、101-500位で20.9%（上位が高い）')
add_bullet('芳醇系: Top10で18.4%、101-500位で25.0%（むしろ上位が低い）')

doc.add_heading('Top10銘柄の味わいプロファイル', level=2)
add_text('各銘柄のレビューからキーワード出現率をレーダーチャートにした。')
add_image('fig4_verification_radar.png', '図4: Top10銘柄の味わいプロファイル。花陽浴のフルーティ率37%が突出。')
add_text('花陽浴のフルーティ率37%、陽乃鳥・宮寒梅の甘口率44%が目立つ。一方、十四代は辛口率わずか1.8%で、バランスの良さが特徴。')

doc.add_heading('テイスト分布のヒートマップ', level=2)
add_text('ボディ（縦軸）× 甘辛（横軸）のクロス集計を、ランキング帯別に比較した。')
add_image('fig5_verification_heatmap.png', '図5: テイスト分布の比較。Top10は「普通ボディ×甘い+1」に集中。')
add_text('Top10は「ボディ:普通 × 甘辛:甘い+1」のゾーンに集中している。つまり、「重厚で芳醇」ではなく「適度な軽さの甘口」が上位の典型的なプロファイルだ。')

doc.add_heading('この検証の結論', level=2)
add_text('「上位ランキングの日本酒は甘口で芳醇」という主張は部分的に正しい。より正確に言えば：')
add_quote('上位ランキングの日本酒は「甘口でフルーティ、ボディは普通〜やや軽めで上品」なものが多い。')

add_separator()

# --- 分析3 ---
doc.add_heading('分析3: この傾向は年々強まっているのか？', level=1)
add_text('SAKETIMEのレビューデータは2017年〜2025年をカバーしている。この期間でのトレンド変化を検証した。')

doc.add_heading('構造化データの時系列推移', level=2)
add_image('fig6_trend_structured.png', '図6: テイスト傾向の時系列推移（構造化データ）')
add_bullet('甘口率は高水準で安定（上位50位: 54-60%で推移）')
add_bullet('辛口率は全体で下降傾向（15%→11%）')
add_bullet('濃醇率は明確に下降（17%→8%に半減）― 「重い酒」離れが進行中')

doc.add_heading('テキスト分析の時系列推移', level=2)
add_image('fig7_trend_text.png', '図7: 味わいキーワード出現率の推移（テキスト分析）')
add_text('最も顕著な変化はフルーティ系キーワードの増加だ。上位50位では2017年の18%から2025年の28%へ、10ポイント上昇している。甘口は2019年頃に一段階上がった後は安定しており、「強まっている」というよりは「既に主流として定着した」と言える。')

add_separator()

# --- 分析4 ---
doc.add_heading('分析4: 140年の大きな流れで見る', level=1)
add_text('SAKETIMEのデータだけでは2017年以降しかカバーできない。より長い歴史的スパンで日本酒の味わいトレンドを見るため、2つの追加データソースを活用した。')

doc.add_heading('国立国会図書館のNDL Ngram Viewer（1880年代〜2000年）', level=2)
add_text('国立国会図書館が提供するNDL Ngram Viewerは、約230万点の図書・雑誌のOCRテキストから、キーワードの出現頻度を年代別に可視化できるツールだ。「辛口」「甘口」「淡麗」「芳醇」「吟醸」「純米」の出現比率を追った。')

# 注記
p = doc.add_paragraph()
p.paragraph_format.left_indent = Cm(0.8)
p.paragraph_format.space_before = Pt(8)
p.paragraph_format.space_after = Pt(8)
run = p.add_run('【注意】NDL Ngram Viewerのデータは全出版物における単語の出現頻度であり、日本酒の文脈に限定されていない。たとえば「辛口」には批評の「辛口コメント」、「甘口」にはカレーの「甘口」なども含まれる。日本酒固有の語である「淡麗」「芳醇」「吟醸」「純米」は比較的日本酒文脈に近いと考えられるが、厳密には日本酒以外の用法も含まれる点に留意されたい。あくまで長期的なトレンドの参考値として解釈すべきデータである。')
run.font.name = 'Yu Gothic'
run.font.size = Pt(9.5)
run.font.italic = True
run.font.color.rgb = RGBColor(100, 100, 100)

add_image('fig8_ndl_ngram.png', '図8: 出版物における味わい語の出現比率（1880〜2000年）。出典: NDL Ngram Viewer。日本酒以外の文脈も含む。')
add_text('明治時代（1880年代）には「甘口」が出版物で多く使われていた。その後100年かけて減少し、代わりに1970年代から「辛口」が急上昇する。これは「淡麗辛口ブーム」と時期が一致する。「辛口」には日本酒以外の用法も含まれるが、同時期に日本酒固有の語である「淡麗」も上昇していることから、日本酒の辛口ブームがこの上昇に寄与していると推測できる。下段では「吟醸」が1980年代から爆発的に増加しており、吟醸酒ブームの実態がデータで裏付けられた。')

doc.add_heading('Google Trends（2004年〜2025年）', level=2)
add_text('NDLのデータが2000年頃で途切れるため、Google Trendsで2004年以降の検索トレンドを補完した。')
add_image('fig9_google_trends.png', '図9: Google Trendsにおける日本酒関連の検索トレンド（2004〜2025年）')
add_text('興味深いのは、Google検索では「日本酒 辛口」が一貫して「日本酒 甘口」の2.5倍の検索量を維持していることだ。NDLのデータとは異なり、Google Trendsでは「日本酒」との組み合わせで検索しているため、日本酒の文脈に限定されたデータである。SAKETIMEの愛好家コミュニティでは甘口・フルーティが主流なのに、一般消費者の検索行動ではまだ「辛口」が主要キーワードなのだ。')
add_text('これは日本酒の味わいトレンドに「二重構造」があることを示唆している：')
add_bullet('愛好家層（SAKETIMEレビュアー）：甘口・フルーティ・軽快が主流')
add_bullet('一般消費者層（Google検索）：依然として「辛口」を軸に日本酒を探している')

add_separator()

# --- まとめ ---
doc.add_heading('まとめ: 140年のサイクル', level=1)
add_text('3つのデータソースを時系列で接続すると、日本酒の味わいトレンドの大きなサイクルが浮かび上がる。ただし、各データソースには性質の違い（NDLは全出版物の語頻度、Google Trendsは検索語の組み合わせ、SAKETIMEは愛好家のレビュー）があり、単純な比較には注意が必要だ。その点を踏まえた上で、大きな流れとしては以下のように読み取れる。')
add_bullet('1880年代〜: 甘口の時代（出版物で「甘口」が圧倒的）')
add_bullet('1970年代〜90年代: 淡麗辛口ブーム（「辛口」「吟醸」が急上昇）')
add_bullet('2000年代〜: 純米吟醸ブーム（Google検索で急上昇）')
add_bullet('2010年代後半〜: 甘口・フルーティ回帰（SAKETIMEレビューで顕著）')
add_text('約140年をかけて、甘口→辛口→甘口（フルーティ）という大きな揺り戻しが起きている。ただし、現在の「甘口回帰」は明治の甘口とは異なり、フルーティで軽快、上品な甘さという新しい文脈の中で起きている。')
add_text('そして最も重要な発見は、この変化が愛好家層から先行して起きているということだ。SAKETIMEのランキング上位はすでに甘口・フルーティ・軽快に収束しつつあるが、一般消費者のGoogle検索ではまだ「辛口」が主要語である。この「愛好家と一般層のギャップ」が今後縮まっていくのか、それとも棲み分けとして定着するのかは、今後の日本酒市場の行方を占う重要なポイントだろう。')

add_separator()

# --- 分析手法 ---
doc.add_heading('分析手法について', level=1)
add_bullet('SAKETIMEデータ: Pythonによるスクレイピング（BeautifulSoup）。5,386銘柄のランキング情報、銘柄詳細、約18万件のレビューを取得')
add_bullet('テキスト分析: キーワード出現率の集計、ランキング帯別・年代別クロス分析')
add_bullet('出版物データ: 国立国会図書館 NDL Ngram Viewer API（図書・雑誌約230万点のOCRテキスト）')
add_bullet('検索トレンド: Google Trends（pytrends、地域:日本、2004年〜2025年）')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(12)
run = p.add_run('データ取得日: 2026年4月14日')
run.font.size = Pt(9)
run.font.color.rgb = RGBColor(130, 130, 130)
run.font.name = 'Yu Gothic'

# 保存
output_path = os.path.join(BLOG_DIR, 'article.docx')
doc.save(output_path)
print(f'保存完了: {output_path}')

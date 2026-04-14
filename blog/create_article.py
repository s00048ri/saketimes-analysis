"""ブログ記事をWord文書として作成（新構成版）"""
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
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

section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
for attr in ['left_margin', 'right_margin', 'top_margin', 'bottom_margin']:
    setattr(section, attr, Cm(2.5))

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
        r = p2.add_run(subtitle)
        r.font.size = Pt(10)
        r.font.italic = True
        r.font.color.rgb = RGBColor(100, 100, 100)
        r.font.name = 'Yu Gothic'

def add_text(text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Yu Gothic'
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

def add_bullet(text):
    p = doc.add_paragraph(text, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Yu Gothic'

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

def add_note(text):
    """注記（グレーのイタリック）"""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    run.font.name = 'Yu Gothic'
    run.font.size = Pt(9.5)
    run.font.italic = True
    run.font.color.rgb = RGBColor(100, 100, 100)

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
    '「"辛口がいい酒"の時代は終わったか？」',
    '― 140年分のデータが示す意外な答え'
)

add_text('「日本酒は辛口がうまい」―― 居酒屋でもよく聞くこのフレーズ。しかし最近、日本酒レビューサイトのランキング上位を占めるのは甘口でフルーティな銘柄ばかりだ。辛口の時代は本当に終わったのか？ 国立国会図書館の出版物データ、日本酒レビューサイトSAKETIMEの約37万件のレビュー、そしてGoogle Trendsの検索データを横断分析し、140年のスパンで答えを探った。')

add_separator()

# ===== きっかけ =====
doc.add_heading('きっかけ：あるYouTube動画の主張', level=1)

add_text('きっかけはYouTubeの日本酒動画だった。その動画では、日本最大級の日本酒レビューサイト「SAKETIME」のランキングを見て、「上位に入る日本酒は、甘口で芳醇なものが多い」という結論に達していた。')

add_text('直感的にはそうかもしれない。しかし、本当にデータで裏付けられるのだろうか？ そして、もしランキング上位が甘口ばかりだとしたら、あの「辛口がいい酒」という長年の常識はどうなったのか？')

add_text('そこで、SAKETIMEの全5,386銘柄・約37万件のレビューをスクレイピングし、体系的に検証することにした。さらに、「辛口信仰」がそもそもいつ始まったのかを、国立国会図書館の出版物データやGoogle Trendsで140年のスパンで追ってみた。')

add_separator()

# ===== 第1章 =====
doc.add_heading('第1章：「辛口がいい酒」はいつ始まったのか', level=1)

add_text('まず、長い歴史のスパンで見てみよう。国立国会図書館が提供するNDL Ngram Viewerは、約230万点の図書・雑誌のOCRテキストから、キーワードの出現頻度を年代別に可視化できるツールだ。「辛口」「甘口」「淡麗」「芳醇」「吟醸」「純米」の出現比率を1880年代から追った。')

add_note('【注意】NDL Ngram Viewerのデータは全出版物における単語の出現頻度であり、日本酒の文脈に限定されていない。たとえば「辛口」には批評の「辛口コメント」、「甘口」にはカレーの「甘口」なども含まれる。日本酒固有の語である「淡麗」「吟醸」「純米」は比較的日本酒文脈に近いと考えられるが、厳密には他の用法も含まれる点に留意されたい。あくまで長期的なトレンドの参考値として解釈すべきデータである。')

add_image('fig8_ndl_ngram.png', '図1: 出版物における味わい語の出現比率（1880〜2000年）。出典: NDL Ngram Viewer。日本酒以外の文脈も含む。')

add_text('結果は驚くべきものだった。明治時代（1880年代）には、「甘口」が出版物で圧倒的に多く使われていた。つまり、日本酒の味わいの語りはもともと「甘口」が中心だったのだ。')

add_text('「甘口」はその後100年かけて緩やかに減少し、代わりに1970年代から「辛口」が急上昇する。同時期に日本酒固有の語である「淡麗」も上昇していることから、これは日本酒の「淡麗辛口ブーム」の到来を反映していると推測できる。')

add_text('下段のグラフでは、「吟醸」が1980年代から爆発的に増加している。吟醸酒ブームの実態がデータで裏付けられた格好だ。「辛口がいい酒」という信仰は、実はこの1970年代〜80年代に形成された、歴史的に見れば比較的新しい価値観なのである。')

add_separator()

# ===== 第2章 =====
doc.add_heading('第2章：いま、ランキング上位を占めるのはどんな酒か', level=1)

add_text('では、現在の日本酒レビューサイトではどうなっているのか。SAKETIMEの全5,386銘柄のランキングデータを分析した。')

doc.add_heading('ランキングの全体像', level=2)

add_text('評価スコアの平均は3.18（5点満点）で、大半が3.0前後に集中している。注目すべきは、レビュー数（対数スケール）と評価の相関が0.888と非常に高いこと。多くのレビューを集める銘柄ほど高評価を得ている。')

add_image('fig1_rating_vs_reviews.png', '図2: 評価スコア vs レビュー数。上位10銘柄をラベル表示。')

doc.add_heading('構造化データ：上位ほど甘口、しかし「芳醇」ではない', level=2)

add_text('SAKETIMEではレビュー時に「甘辛」（辛い+2〜甘い+2の5段階）と「ボディ」（軽い+2〜重い+2の5段階）を選択できる。これをランキング帯別に集計した結果、明確な傾向が見えた。')

add_image('fig2_verification_structured.png', '図3: ランキング帯別の甘口率と濃醇率。')

add_bullet('甘口率（甘い+1以上）: Top10で67.3%、101-500位で30.2%、501位以降で27.6%')
add_bullet('辛口率（辛い+1以上）: Top10でわずか3.7%、101-500位で25.7%、501位以降で29.3%')
add_bullet('濃醇率（重い+1以上）: Top10で11.2%、101-500位で18.4% → 上位ほどむしろ軽い')

add_text('甘口率はTop10（67%）と501位以降（28%）で実に40ポイントもの差がある。逆に辛口率を見ると、501位以降（29%）はTop10（4%）の7倍以上だ。ランキングの上位と下位では、「甘口の世界」と「辛口の世界」がはっきりと分かれている。')

add_text('YouTube動画の「甘口」という指摘は正しかったが、「芳醇」は誤りだった。上位銘柄は甘口だが、ボディは重厚ではなく普通〜やや軽めなのだ。')

doc.add_heading('テキスト分析：浮かび上がる「フルーティ」の存在感', level=2)

add_text('約37万件のレビューテキストから味わいキーワードの出現率をランキング帯別に比較すると、もう一つの特徴が見えてきた。')

add_image('fig3_verification_text.png', '図4: レビューテキスト中の味わいキーワード出現率（ランキング帯別）')

add_bullet('甘口系キーワード: Top10で32.8%、501位以降で26.8%')
add_bullet('辛口系キーワード: Top10で3.7%、501位以降で16.8%（上位ほど圧倒的に少ない）')
add_bullet('フルーティ系: Top10で24.7%、501位以降で13.3%（上位で約2倍）')
add_bullet('芳醇系: Top10で17.9%、501位以降で23.2%（むしろ上位が低い）')

add_text('Top10銘柄の味わいプロファイルをレーダーチャートにすると、各銘柄の個性が浮かび上がる。')

add_image('fig4_verification_radar.png', '図5: Top10銘柄の味わいプロファイル。花陽浴のフルーティ率37%が突出。')

add_text('花陽浴のフルーティ率37%、陽乃鳥・宮寒梅の甘口率44%が際立つ。一方、ランキング1位の十四代は辛口率わずか1.8%で、突出した偏りがなくバランスの良さが特徴だ。')

doc.add_heading('テイスト分布：上位の「典型的プロファイル」', level=2)

add_text('ボディ × 甘辛のクロス集計をヒートマップにすると、上位銘柄の味わいの中心地が見える。')

add_image('fig5_verification_heatmap.png', '図6: テイスト分布の比較。Top10は「普通ボディ×甘い+1」に集中。')

add_quote('いまのランキング上位は「甘口でフルーティ、ボディは普通〜やや軽めで上品」。「重厚で芳醇」ではなく「適度な軽さの甘口」が上位の典型だ。')

add_separator()

# ===== 第3章 =====
doc.add_heading('第3章：この変化はいつから起きているのか', level=1)

add_text('SAKETIMEのレビューデータは2017年〜2025年をカバーしている。この期間でのトレンド変化を追った。')

doc.add_heading('構造化データの時系列推移', level=2)

add_image('fig6_trend_structured.png', '図7: テイスト傾向の時系列推移（構造化データ）')

add_bullet('甘口率は高水準で安定（上位50位: 54-60%で推移）')
add_bullet('辛口率は全体で下降傾向（15%→11%）')
add_bullet('濃醇率は明確に下降（17%→8%に半減）― 「重い酒」離れが進行中')

doc.add_heading('テキスト分析の時系列推移', level=2)

add_image('fig7_trend_text.png', '図8: 味わいキーワード出現率の推移（テキスト分析）')

add_text('最も顕著な変化はフルーティ系キーワードの増加だ。上位50位では2017年の18%から2025年の28%へ、10ポイント上昇している。')

add_text('甘口は2019年頃に一段階上がった後は安定しており、「いま強まっている」というよりは「既に主流として定着した」と言える方が正確だ。一方、フルーティという表現は現在進行形で増え続けている。')

add_separator()

# ===== 第4章 =====
doc.add_heading('第4章：では「辛口の時代」は終わったのか？ ― 意外な答え', level=1)

add_text('ここまでのデータを見ると、「辛口の時代は終わった」と結論づけたくなる。愛好家のレビューサイトでは甘口・フルーティが主流になり、辛口のキーワードは減少傾向にある。')

add_text('しかし、もう一つのデータソースが、まったく異なる景色を見せてくれる。')

doc.add_heading('Google Trendsが示す一般消費者のリアル', level=2)

add_text('NDLのデータが2000年頃で途切れるため、Google Trendsで2004年以降の検索トレンドを確認した。NDLのデータとは異なり、Google Trendsでは「日本酒」との組み合わせで検索しているため、日本酒の文脈に限定されたデータである。')

add_image('fig9_google_trends.png', '図9: Google Trendsにおける日本酒関連の検索トレンド（2004〜2025年）')

add_text('結果は衝撃的だった。Google検索では「日本酒 辛口」が「日本酒 甘口」の約2.5倍の検索量を一貫して維持しているのだ。しかも、辛口の検索量は減るどころか、2004年から2025年にかけて右肩上がりで増え続けている。')

add_text('つまり、一般消費者が日本酒を探すとき、いまだに「辛口」が最も重要なキーワードなのだ。')

doc.add_heading('二つの世界', level=2)

add_quote('辛口の時代は「終わっていない」。しかし、「二つの世界」が生まれている。')

add_bullet('愛好家の世界（SAKETIMEレビュアー）：甘口・フルーティ・軽快が主流。上位ランキングは甘口に収束しつつある。')
add_bullet('一般消費者の世界（Google検索）：依然として「辛口」が日本酒を選ぶ際の主要キーワード。その検索量はむしろ増加中。')

add_text('興味深いことに、この分断はSAKETIMEの中にも存在する。同じレビューサイトの中でも、ランキング上位（甘口率67%、辛口率4%）と501位以降（甘口率28%、辛口率29%）では、まるで別の世界だ。愛好家が注目する上位銘柄は甘口・フルーティの世界だが、全体を俯瞰すれば辛口の銘柄も数多く存在している。')

add_text('日本酒の味わいトレンドには「二重構造」が存在している。愛好家コミュニティの注目銘柄ではとっくに甘口・フルーティへのシフトが起きているのに、一般消費者の検索行動ではまだ「辛口」が軸なのだ。')

add_separator()

# ===== まとめ =====
doc.add_heading('まとめ：140年のサイクルと、いま起きている分断', level=1)

add_text('3つのデータソースを時系列で接続すると、日本酒の味わいトレンドの大きなサイクルが浮かび上がる。ただし、各データソースには性質の違い（NDLは全出版物の語頻度、Google Trendsは検索語の組み合わせ、SAKETIMEは愛好家のレビュー）があり、単純な比較には注意が必要だ。その点を踏まえた上で、大きな流れとしては以下のように読み取れる。')

add_bullet('1880年代〜：甘口の時代（出版物で「甘口」が圧倒的）')
add_bullet('1970年代〜90年代：淡麗辛口ブーム（「辛口」「吟醸」が急上昇）')
add_bullet('2000年代〜：純米吟醸ブーム（Google検索で急上昇）')
add_bullet('2010年代後半〜：甘口・フルーティ回帰（SAKETIMEレビューで顕著）')

add_text('約140年をかけて、甘口→辛口→甘口（フルーティ）という大きな揺り戻しが起きている。ただし、現在の「甘口回帰」は明治の甘口とは異なり、フルーティで軽快、上品な甘さという新しい文脈の中で起きている。')

add_text('そして最も重要な発見は、この変化が愛好家層から先行して起きているということだ。SAKETIMEのランキング上位はすでに甘口・フルーティ・軽快に収束しつつあるが、一般消費者のGoogle検索では「辛口」がいまも主役であり、その検索量は増え続けている。')

add_text('この「愛好家と一般層のギャップ」が今後縮まっていくのか、それとも棲み分けとして定着するのか。それは、日本酒市場の行方を占う重要な問いだろう。')

add_separator()

# ===== 分析手法 =====
doc.add_heading('分析手法について', level=1)
add_bullet('SAKETIMEデータ: Pythonによるスクレイピング（BeautifulSoup）。5,386銘柄のランキング情報、銘柄詳細、約37万件のレビューを取得')
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

"""Medium の Import a story 用に Markdown を絶対 URL 付き HTML に変換する。

Medium のインポート機能:
    https://medium.com/p/import → URL を貼ると HTML をパースし、Medium の
    エディタブロックに変換してくれる。画像は HTML 内の <img src="https://..."> から
    絶対 URL でフェッチされるので、画像を GitHub Pages 等で配信する必要がある。

Usage:
    python3 scripts/render_for_medium.py blog/article_en_acidity.md \\
        --image-base https://s00048ri.github.io/saketimes-analysis/blog/medium_acidity

出力:
    入力と同じディレクトリに <stem>.html を生成する。
    Medium の Import a story で、GitHub Pages 上にプッシュした HTML の URL を渡す。

設計判断:
    - 画像は **絶対 URL** (base64 ではなく). Medium は import 時にフェッチして自前
      の CDN に転載する
    - H1 にタイトルが含まれる場合、em-dash (—) で分割があれば前半を <h1>、
      後半を <h3> サブタイトルとして書く (Medium の規約)
    - 見出し下に <hr/> は入れない (Medium は import 時に sections を自動分離)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import markdown

DEFAULT_IMAGE_BASE = (
    "https://s00048ri.github.io/saketimes-analysis/blog/medium_acidity"
)


def split_title(html_body: str) -> str:
    """最初の <h1>title — subtitle</h1> を <h1>title</h1><h3>Subtitle</h3> に分割する。

    サブタイトル側は先頭1文字を大文字化（em-dash 後の続き句が小文字始まりでも
    Medium の見出しとして自然になるよう補正）。
    """
    pattern = re.compile(r"<h1>([^<]+?)\s*[——]\s*([^<]+?)</h1>", re.DOTALL)

    def replace(m: re.Match) -> str:
        title = m.group(1).strip()
        subtitle = m.group(2).strip()
        if subtitle and subtitle[0].islower():
            subtitle = subtitle[0].upper() + subtitle[1:]
        return f"<h1>{title}</h1>\n<h3>{subtitle}</h3>"

    return pattern.sub(replace, html_body, count=1)


def rewrite_img_src(html_body: str, image_base: str) -> str:
    """<img src="local.png"> を <img src="{image_base}/local.png"> に置換する。

    既に http(s):// で始まる src はスキップ。
    """
    def replace(match: re.Match) -> str:
        prefix, src, suffix = match.group(1), match.group(2), match.group(3)
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)
        filename = Path(src).name
        return f'{prefix}{image_base}/{filename}{suffix}'

    pattern = re.compile(r'(<img[^>]+src=")([^"]+)("[^>]*>)')
    return pattern.sub(replace, html_body)


def render(md_path: Path, image_base: str) -> Path:
    md_text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["extra", "tables", "sane_lists"],
        output_format="html5",
    )
    html_body = split_title(html_body)
    html_body = rewrite_img_src(html_body, image_base)

    # 抽出されたタイトル (h1) を <title> にも入れる
    title_match = re.search(r"<h1>([^<]+)</h1>", html_body)
    page_title = title_match.group(1) if title_match else md_path.stem

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{page_title}</title>
</head>
<body>
<article>
{html_body}
</article>
</body>
</html>
"""
    out = md_path.parent / f"{md_path.stem}.html"
    out.write_text(html, encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("md_file", help="入力 Markdown ファイル")
    parser.add_argument(
        "--image-base",
        default=DEFAULT_IMAGE_BASE,
        help=f"画像 URL のベース (default: {DEFAULT_IMAGE_BASE})",
    )
    args = parser.parse_args()

    md_path = Path(args.md_file).resolve()
    if not md_path.is_file():
        print(f"Not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    out = render(md_path, args.image_base.rstrip("/"))
    size_kb = out.stat().st_size // 1024
    img_count = out.read_text(encoding="utf-8").count("<img")
    print(f"wrote: {out}")
    print(f"  size: {size_kb} KB,  embedded <img>: {img_count}")
    print(f"  image base: {args.image_base}")


if __name__ == "__main__":
    main()

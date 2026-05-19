"""note.com 投稿用に Markdown を自己完結 HTML にレンダリングする。

なぜ必要か:
    note のエディタは Markdown を解釈しない。代わりに、ブラウザのページから
    Cmd+A → Cmd+C → note にペーストすると、リッチテキスト (見出し・太字・
    リスト) はそのまま転送される。ただし、画像は VSCode プレビューや相対
    パスの HTML では「vscode-resource:// や file://」スキームで参照される
    ためクリップボードに画像バイナリが乗らない。

このスクリプトは画像を `data:image/png;base64,...` として HTML に埋め込む
ことで、通常のブラウザで開いた段階で画像が完全にメモリ上に読み込まれた
状態になる。コピー時にクリップボードに画像バイナリが乗るため、note エディタ
側で個別アップロードなしに貼り付けられる。

Usage:
    python3 scripts/render_for_note.py blog/article_jp_acidity_note.md

出力:
    入力と同じディレクトリに <stem>_for_note.html を生成し、ブラウザで開く。
"""
from __future__ import annotations

import base64
import mimetypes
import re
import subprocess
import sys
from pathlib import Path

import markdown

NOTE_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont,
        "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif;
    max-width: 660px;
    margin: 40px auto;
    padding: 0 20px;
    line-height: 1.85;
    color: #1f1f1f;
    font-size: 17px;
}
h1 { font-size: 1.85em; margin: 1.2em 0 0.8em; line-height: 1.35; }
h2 {
    font-size: 1.40em;
    margin: 2.2em 0 0.8em;
    padding-bottom: 0.25em;
    border-bottom: 1px solid #e0e0e0;
}
h3 { font-size: 1.18em; margin: 1.8em 0 0.6em; }
p { margin: 0.9em 0; }
ul, ol { margin: 0.9em 0; padding-left: 1.4em; }
li { margin: 0.25em 0; }
blockquote {
    border-left: 4px solid #ccc;
    padding: 0.6em 1em;
    color: #555;
    background: #f7f7f7;
    margin: 1.2em 0;
}
blockquote p { margin: 0.3em 0; }
table { border-collapse: collapse; margin: 1.2em 0; width: 100%; }
th, td { border: 1px solid #ddd; padding: 6px 12px; text-align: left; }
th { background: #f0f0f0; }
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1.5em auto 0.3em;
}
img + em, p > em:only-child {
    display: block;
    text-align: center;
    color: #888;
    font-size: 0.9em;
    margin-bottom: 1.5em;
}
em { color: #555; }
strong { color: #111; }
a { color: #1976D2; text-decoration: underline; }
code {
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.92em;
    font-family: "SF Mono", Monaco, Consolas, monospace;
}
hr { border: none; border-top: 1px solid #ddd; margin: 2.5em 0; }
"""


def embed_image(match: re.Match, base_dir: Path) -> str:
    prefix, src, suffix = match.group(1), match.group(2), match.group(3)
    if src.startswith(("data:", "http://", "https://")):
        return match.group(0)
    img_path = (base_dir / src).resolve()
    if not img_path.is_file():
        print(f"WARN: image not found: {img_path}", file=sys.stderr)
        return match.group(0)
    mime, _ = mimetypes.guess_type(str(img_path))
    if mime is None:
        mime = "image/png"
    b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
    return f'{prefix}data:{mime};base64,{b64}{suffix}'


def render(md_path: Path) -> Path:
    md_text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["extra", "tables", "sane_lists", "nl2br"],
    )
    pattern = re.compile(r'(<img[^>]+src=")([^"]+)("[^>]*>)')
    html_body = pattern.sub(lambda m: embed_image(m, md_path.parent), html_body)

    title = md_path.stem
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{NOTE_CSS}</style>
</head>
<body>
{html_body}
</body>
</html>
"""
    out = md_path.parent / f"{md_path.stem}_for_note.html"
    out.write_text(html, encoding="utf-8")
    return out


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/render_for_note.py <input.md>",
              file=sys.stderr)
        sys.exit(1)
    md_path = Path(sys.argv[1]).resolve()
    if not md_path.is_file():
        print(f"Not found: {md_path}", file=sys.stderr)
        sys.exit(1)
    out = render(md_path)
    size_kb = out.stat().st_size // 1024
    print(f"wrote: {out}  ({size_kb} KB)")
    subprocess.run(["open", str(out)], check=False)


if __name__ == "__main__":
    main()

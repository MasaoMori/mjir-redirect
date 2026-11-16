#!/usr/bin/env python3
"""mjir.info の旧URLを https://jairweb.jp/ に転送するページを生成する。
使い方: python3 -I scripts/generate.py <jair-mjir のパス> [出力先(省略時はこのリポジトリのルート)]
  - jair-mjir/content の origin: mjir のページ・投稿 → 同じパスの jairweb.jp に転送
  - jair-mjir/static/wp-content/uploads/filebase/* → /download/* の旧URLから新URLへ転送
  - それ以外(404.html): /wp-content/ は同じパスへ、ほかは https://jairweb.jp/conference/ へ
再実行すると、生成済みの転送ページ(下の MARK 入り)を作り直す。
"""
import re, sys, html, shutil, urllib.parse as up
from pathlib import Path

SRC = Path(sys.argv[1]).expanduser()
OUT = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent
DEST = "https://jairweb.jp"
FALLBACK = DEST + "/conference/"
MARK = "<!-- mjir-redirect:generated -->"

def page(target, title="転送中"):
    t = html.escape(target, quote=True)
    js = target.replace("\\", "\\\\").replace('"', '\\"')
    return f"""<!doctype html>
{MARK}
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="canonical" href="{t}">
<meta http-equiv="refresh" content="0; url={t}">
<script>location.replace("{js}");</script>
</head><body><p>新しいページへ移動します: <a href="{t}">{t}</a></p></body></html>
"""

# 以前に生成したものを削除(index.html と 404.html は後で作り直す)
for p in list(OUT.rglob("index.html")) + [OUT / "404.html"]:
    if p.exists() and MARK in p.read_text(encoding="utf-8", errors="ignore")[:200]:
        p.unlink()
for d in sorted([d for d in OUT.rglob("*") if d.is_dir() and ".git" not in d.parts], reverse=True):
    if not any(d.iterdir()): d.rmdir()

routes = {}  # 旧パス(末尾 / つき) -> 転送先パス
# 1) 記事・ページ
for f in list((SRC/"content").rglob("*.md")) + list((SRC/"content").rglob("*.html")):
    head = f.read_text(encoding="utf-8")[:3000]
    o = re.search(r'^origin:\s*"?(\w+)', head, re.M)
    u = re.search(r'^url:\s*"?([^"\n]+?)"?\s*$', head, re.M)
    if o and o.group(1) == "mjir" and u:
        p = u.group(1)
        if not p.endswith("/"): p += "/"
        routes[p] = p
# 2) 論文PDFなど(旧 /download/ → 新 /wp-content/uploads/filebase/)
fb = SRC/"static/wp-content/uploads/filebase"
for f in fb.rglob("*"):
    if f.is_file() and not f.name.startswith("."):
        rel = f.relative_to(fb).as_posix()
        routes["/download/" + rel + "/"] = "/wp-content/uploads/filebase/" + rel

routes.pop("/", None)
for old, new in sorted(routes.items()):
    d = OUT / old.strip("/")
    d.mkdir(parents=True, exist_ok=True)
    (d/"index.html").write_text(page(DEST + up.quote(new, safe="/%~-._")), encoding="utf-8")

(OUT/"index.html").write_text(page(FALLBACK), encoding="utf-8")
(OUT/"404.html").write_text(f"""<!doctype html>
{MARK}
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>
(function () {{
  var p = location.pathname, q = location.search + location.hash;
  // 旧 WordPress のアップロードファイルは、同じパスの jairweb.jp にある
  if (p.indexOf("/wp-content/") === 0) location.replace("{DEST}" + p + q);
  else location.replace("{FALLBACK}");
}})();
</script>
<noscript><meta http-equiv="refresh" content="0; url={FALLBACK}"></noscript>
</head><body><p>新しいサイトへ移動します: <a href="{FALLBACK}">{FALLBACK}</a></p></body></html>
""", encoding="utf-8")
print(f"転送ページ {len(routes)} 件(記事・ページ {sum(1 for k in routes if not k.startswith('/download/'))}、PDFなど {sum(1 for k in routes if k.startswith('/download/'))})")

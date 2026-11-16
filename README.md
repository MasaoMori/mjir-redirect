# mjir-redirect

`mjir.info` へのアクセスを、統合サイト <https://jairweb.jp/> に転送するための、転送専用のリポジトリ(GitHub Pages)。
サイトの内容は持たない。統合サイトは [MasaoMori/jair-mjir](https://github.com/MasaoMori/jair-mjir)。

## 転送の規則
| 旧URL(mjir.info) | 転送先(jairweb.jp) |
|---|---|
| `/` と、下記以外のURL | `/conference/` |
| MJIR の旧記事・旧ページ(139件。例: `/2016/05/18/第5回mjirプログラム発表/`) | 同じパス |
| `/download/articles_YYYY/X.pdf` など、旧論文PDF(148件) | `/wp-content/uploads/filebase/articles_YYYY/X.pdf` |
| `/wp-content/…`(旧アップロードファイル) | 同じパス(`404.html` の JavaScript による) |

GitHub Pages は 301 を返せないため、HTML の `<meta refresh>` と JavaScript で転送する。

## 作り直し
`jair-mjir` の記事・PDF を足したり、置き場所を変えたりしたときだけ、作り直す。
```bash
python3 -I scripts/generate.py <jair-mjir のパス>
```
`origin: mjir` の記事・ページと、`static/wp-content/uploads/filebase/` のファイルから、転送ページを生成する(生成済みのものは作り直す)。

## 独自ドメイン
DNS を切り替えるときに、Pages の独自ドメインを `mjir.info` に設定する(手順は `jair-mjir` 側の `独自ドメイン手順.md`)。

# 介護福祉士の日記w

GitHub PagesとJekyllで公開する静的ブログです。記事はMarkdownファイルとして残るため、サイトとは別に原稿そのものを保管できます。

## 記事を書く

1. `_posts` フォルダに `年-月-日-英数字の名前.md` というファイルを作ります。
2. 下の見本を貼り、題名・日付・カテゴリ・本文を変更します。
3. GitHubへ反映すると、サイトが自動更新されます。

```markdown
---
title: "記事の題名"
date: 2026-07-14 20:00:00 +0900
categories: [介護日記]
excerpt: "一覧に表示する短い紹介文です。"
---

ここから本文を書きます。
```

## GitHub Pagesで公開する

1. このフォルダをGitHubの公開リポジトリへ送ります。
2. リポジトリの `Settings` → `Pages` を開きます。
3. `Build and deployment` のSourceで `Deploy from a branch` を選びます。
4. Branchを `main`、フォルダを `/(root)` にして保存します。

プロジェクトサイト（URL末尾にリポジトリ名が付く形式）でも動作するよう、内部リンクにはJekyllの `relative_url` を使用しています。

## 手元で確認する

RubyとBundlerが使える環境で実行します。

```bash
bundle install
bundle exec jekyll serve
```

表示された `http://127.0.0.1:4000` をブラウザで開きます。

## Seesaaから移した記事

2026年7月14日に、2010年4月から2026年7月までのMT形式バックアップを取得しました。

- 公開記事: 2,044件
- 非公開記事: 75件（サイトには出力しない）
- 公開コメント: 273件（名前・日時・本文のみ出力）
- カテゴリ: 76件
- 保存できた本人画像: 44ファイル
- 元サービスですでに404だった画像URL: 94件

MTバックアップと画像取得エラーの詳細は `private-backup/` に置いています。このフォルダにはコメント投稿者のメールアドレスやIPが含まれる可能性があるため、`.gitignore` でGitHubの対象外にしています。

再変換するときは、次の順番で実行します。

```bash
python3 scripts/audit_public_drafts.py
python3 scripts/import_seesaa_mt.py
python3 scripts/download_archive_media.py
bundle exec jekyll build
```

`audit_public_drafts.py` はSeesaa上で公開状態を確認します。MTファイル上で `Draft` になっている記事は、公開URLから実際に読めることが確認できた場合だけ出力対象になります。

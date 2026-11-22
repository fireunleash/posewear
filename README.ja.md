<div align="center">

<img src="docs/banner.jpg" alt="人物 + ポーズ + 服装 = 成果物" width="900">

<sub>成果物は、ギャラリーの人物・ポーズ・服装を参考に AI が生成した例です。素材画像の著作権は各作者に帰属します。謝辞を参照してください。</sub>

<img src="docs/logo.svg" width="72" alt="PoseWear">

# PoseWear 衣姿

バイリンガルのプロンプト付きのポーズ・服装・人物の参考ギャラリーと、ブラウザ上で動作する BYOK（自分の API キーを使う）AI 試着スタジオ。

[![License: MIT](https://img.shields.io/badge/license-MIT-black)](LICENSE)
[![Cloudflare Pages](https://img.shields.io/badge/Cloudflare-Pages-f38020?logo=cloudflare&logoColor=white)](https://pages.cloudflare.com/)
[![Live demo](https://img.shields.io/badge/demo-posewear.pages.dev-ff2442)](https://posewear.pages.dev)
[![GitHub stars](https://img.shields.io/github/stars/atuizz/posewear?style=flat&color=black)](https://github.com/atuizz/posewear/stargazers)

[ライブデモ](https://posewear.pages.dev) · [機能](#機能) · [クイックスタート](#クイックスタート) · [デプロイ](#デプロイ) · [FAQ](#faq) · [中文](README.md) · [English](README.en.md)

<img src="docs/home.jpg" alt="ホーム" width="900">

</div>

## 機能

- **5 つのギャラリー**：ポーズ（多角度の線画）、深度ポーズ（ホットリンクされた深度マップ）、服装（季節と種類で分類）、アニメ服（アニメ風の着こなし）、人物（顔のリファレンス、CC0）。すべての画像に中国語の説明と、コピーできる英語のプロンプトが付いています。
- **検索とフィルター**：中国語または英語で検索、カテゴリーで絞り込み、並べ替え、ランダムな画像の選択ができます。各アイテムには共有用の静的ページがあります。
- **試着スタジオ**：写真をアップロードし、服装とポーズを選んで生成します。写真なしで生成することもできます。1 回の実行で複数の出力、ビフォーアフターのスライダー、単体または zip でのダウンロードに対応しています。
- **生成履歴**：IndexedDB にローカルで保存されます。アイテムの表示、削除、消去、取り消しができます。
- **わかりやすいエラー**：無効なキー、レート制限、タイムアウト、セーフティブロックのそれぞれに専用のメッセージと、次に取るべき手順の提案が表示されます。
- **誤ったセーフティブロックの低減**：既定でオン。スタジオは、服装やポーズを変えずに、プロンプトを中立的な EC 試着の説明に書き換えます。オフにすると、プロンプトをそのまま送信します。
- お気に入り、最近のアイテム、プロンプトの組み合わせはすべてローカルに保存。年齢確認付きの 18+ トグル、PWA とオフライン対応、ダークモード、中国語／英語の UI。

### プロバイダー

| プロバイダー | 必要なもの | 既定のモデル | 備考 |
|---|---|---|---|
| OpenAI | API キー（gpt-image には認証済みの組織が必要） | gpt-image-1 | 複数のリファレンスを使う images/edits。モデレーションが最も厳格 |
| Gemini | Google AI Studio のキー | gemini-2.5-flash-image | 別名 Nano Banana |
| Doubao Seedream | Volcengine Ark のキー | doubao-seedream-4-0-250828 | CORS のため既定でサイトのプロキシ経由 |
| Custom relay | ベース URL、キー、モデル | 任意 | OpenAI 互換。edits（multipart）または generations（JSON）を選択 |

## 変更履歴

### 2026-11-19 · アニメ服ライブラリ

- 新しい **アニメ服** タブ：[@giaaibusi](https://x.com/giaaibusi) による COSTUME-ANIME-DB から 1,320 点のアニメ風の服装を、服装ライブラリと同じ 8 カテゴリー（春 197 / 夏 237 / 秋 230 / 冬 232 / ランジェリー 197 / パーティー 36 / 水着 52 / セクシー 139）で収録。それぞれ中国語と英語のプロンプト付き。
- ランジェリーとセクシーのカテゴリー（336 点）はアダルトコンテンツとして扱われ、既定では 18+ トグルの背後に隠されています（公開アイテムは 984 点）。
- アニメ服は服装の全機能に対応：カテゴリー／色／アイテムのフィルター、検索候補、お気に入り、最近の閲覧、プロンプトの組み合わせ、バイリンガルの詳細ページとサイトマップ。試着スタジオでは、衣装のステップからアニメ服を直接選べます。
- ホームページのお知らせバーとアニメの点数を追加。`scripts/fetch-assets.py` に `anime` ソースを追加（これまで取得できていなかった服装のサムネイルも取得するようになりました）。

### 2026-10-31 · 深度ポーズ

- 新しい **深度ポーズ** タブ：288 セット / 1,439 点のホットリンクされた深度ポーズ画像。2 人の画像は 18+ トグルの背後にあります。

## スクリーンショット

| スタジオ | ダークモード | モバイル |
|:---:|:---:|:---:|
| <img src="docs/studio.jpg" width="420" alt="スタジオ"> | <img src="docs/dark.jpg" width="420" alt="ダークモード"> | <img src="docs/mobile.jpg" width="180" alt="モバイル"> |

## クイックスタート

Pillow を備えた Python 3.9+ が必要です。テストとデプロイには Node.js 18+ も必要です。

```bash
git clone https://github.com/atuizz/posewear.git && cd posewear
pip install pillow
python3 scripts/fetch-assets.py   # 元ギャラリーからデータと画像を取得（数 GB）
python3 scripts/fetch-modules.py  # Shisei（CC0）と CharaDB のタグ。画像はホットリンクのみ
python3 build.py                  # dist/ を出力
python3 -m http.server 8787 -d dist

# wrangler で素の http（例: http://<tailscale-ip>:8787）を開くときは --local を付ける。
# 付けないと _headers の upgrade-insecure-requests と HSTS でブラウザが素材を https に上げ、スタイルが外れる。
# Cloudflare へデプロイするビルドには付けない。
python3 build.py --local          # または POSEWEAR_LOCAL=1 python3 build.py
npx wrangler pages dev dist --ip 0.0.0.0
```

`fetch-modules.py` は髪型・歴代衣装・シーン・光・小道具・家具を埋めます。表情タブは空のままです。WaveSpeed には再配布できる公開パッケージがなく、robots.txt と利用規約 8.5 が画像とデータの収集を禁じています。素材は `assets-raw/` に残り、git には入りません。

別の素材フォルダを使うには `POSEWEAR_RAW` を、サイトマップや共有リンク用に独自のサイト URL を設定するには `POSEWEAR_SITE` を設定します。`POSEWEAR_LOCAL=1`（または `python3 build.py --local`）は `_headers` から HSTS と `upgrade-insecure-requests` を外し、素の http プレビューでも CSS が読めます。

## デプロイ

このリポジトリは素材を含まずに配布されるため、先に `fetch-assets.py` と `fetch-modules.py` を実行し、その後 `dist/` をビルドして Cloudflare Pages にアップロードします：

```bash
npm install && npx wrangler login
POSEWEAR_SITE=https://<project>.pages.dev python3 build.py
npx wrangler pages deploy dist --project-name <project>
```

`functions/api/proxy.js` は、API リクエストを転送するだけの Pages Function としてデプロイされます。`/api/proxy` にレート制限ルールを追加することを推奨します。

## テスト

Playwright のテストはすべてのプロバイダーのエンドポイントをモックするため、実際のキーは不要です。成功、不正なキー、レート制限、5xx エラー、タイムアウト、キャンセル、セーフティブロック、複数出力をカバーします。

```bash
npm install && npx playwright install chromium
python3 -m http.server 8787 -d dist &
node tests/v12.js && node tests/v13.js
```

## FAQ

**API キーは安全ですか？** キーはブラウザの localStorage に保存されます。リクエストはプロバイダーへ直接送られます。プロキシ転送をオンにするか、カスタムリレーを使う場合にのみ `/api/proxy` を経由します。プロキシはリクエストをそのまま転送し、キーや画像を保存することはありません。

**なぜ画像がブロックされたのですか？** プロバイダーは入力写真と出力の両方をモデレーションします。露出の多い服装の実写は最もブロックされやすく、OpenAI が最も厳格です。書き換えオプションは通常の服装での誤検出を減らします。禁止コンテンツのモデレーションを回避するものではありません。

**画像を使えますか？** このリポジトリには画像は含まれていません。すべての素材は各作者に帰属するため、各ソースサイトの規約を確認してください。人物ギャラリーは CC0 です。

## コントリビュート

Issue と PR を歓迎します。PR を出す前に `python3 build.py` と両方のテストファイルを実行し、UI の変更にはスクリーンショットを添えてください。素材やキーはコミットしないでください。

## 謝辞

[AI Pose Gallery](https://ai-pose-gallery.pages.dev/) · [AI Costume Gallery](https://ai-costume-gallery.pages.dev/) · [AI Costume Anime Gallery](https://ai-costume-anime-gallery.pages.dev/) by [@giaaibusi](https://x.com/giaaibusi) · [AI Pose Depth Gallery](https://ai-pose-depth-gallery.pages.dev/) by [ギア / @giaaibusi](https://x.com/giaaibusi)（ホットリンク、非公式の中国語インデックス。画像はこのリポジトリには含まれません） · [AI Portrait Gallery](https://ai-portrait-gallery.pages.dev/) by [@agi_aibusi](https://x.com/agi_aibusi)（CC0） · [Shisei](https://github.com/wquguru/shisei)（歴代衣装・シーン・光・小道具・家具。画像とデータは CC0） · [CharaDB](https://github.com/taki-ttt/charadb)（タグは CC0、画像はホットリンクのみ） · [wzc520pyfm/gen-ai-pose-image](https://github.com/wzc520pyfm/gen-ai-pose-image) · [paipiange/nvzhuang](https://github.com/paipiange/nvzhuang)

## ライセンスと素材の扱い

| 対象 | このリポジトリに含まれる？ | ライセンス |
|---|---|---|
| コード、UI コピー、ビルドスクリプト | はい | [MIT](LICENSE) |
| ポーズと服装の画像・データ | いいえ — `fetch-assets.py` でダウンロード | [@giaaibusi](https://x.com/giaaibusi)（[AI Pose Gallery](https://ai-pose-gallery.pages.dev/) / [AI Costume Gallery](https://ai-costume-gallery.pages.dev/) / [AI Costume Anime Gallery](https://ai-costume-anime-gallery.pages.dev/)）に帰属。オープンライセンスの明示はなし |
| 人物画像 | いいえ — 上と同じ | [@agi_aibusi](https://x.com/agi_aibusi)（[AI Portrait Gallery](https://ai-portrait-gallery.pages.dev/)）による [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| 深度ポーズ画像 | いいえ — [AI Pose Depth Gallery](https://ai-pose-depth-gallery.pages.dev/) から `<img>` でホットリンク | [ギア / @giaaibusi](https://x.com/giaaibusi) に帰属。このリポジトリにはテキストのメタデータと中国語名のみ |
| 深度ポーズのテキストメタデータ | はい、`depth/packs/` | 日本語テキストは原作者に帰属。中国語名は本プロジェクトのもの |
| 歴代衣装・シーン・光・小道具・家具 | いいえ — `fetch-modules.py` が [Shisei](https://github.com/wquguru/shisei) から取得 | 画像と `data/` は [wquguru](https://github.com/wquguru) による [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)。`LICENSE-images` と `NOTICE` を `assets-raw/` に残す |
| 髪型と CharaDB のタグ | いいえ。タグは [taki-ttt/charadb](https://github.com/taki-ttt/charadb) から、画像は [charadb-2fi.pages.dev](https://charadb-2fi.pages.dev/) へホットリンク | タグと日本語名は CC0。画像の再配布は禁止なのでダウンロードしない。第三者の中国語訳には再配布できる許諾がないため、見出しは上流の日本語のまま |
| 表情 | いいえ — 公開手順では作らない | [WaveSpeed AI Emotion Gallery](https://wavespeed.ai/free-tools/ai-emotion-gallery) に再配布できる公開パッケージはない。robots.txt は画像とデータがオープンソースではないと書き、利用規約 8.5 は収集とミラーを禁じる。土台の [ICT-FaceKit](https://github.com/USC-ICT/ICT-FaceKit) は MIT だが、ギャラリーの画像はそれに含まれない |
| README のスクリーンショット | はい | 表示されている画像は上記のとおり各作者に帰属 |

- MIT が対象とするのはコードのみで、画像やデータは対象外です。
- ポーズ／服装の画像を転載、商用利用、再配布する場合は、まず作者 @giaaibusi に確認し、ソースサイトの規約に従ってください。
- 人物画像は CC0 です：クレジット表示なしで自由に使用、改変、販売できます。これらは AI が生成した架空の人物です。実在の人物になりすますために使わないでください。作者は、これらをそのまま大量に転載しないよう求めています。
- 自分でコピーをデプロイする場合は、ページ上のソースと作者のクレジットを残してください。

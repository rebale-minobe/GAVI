# 🌈 GAVI - 英検準2級対策アプリケーション

**Learn English, Enjoy the World**

莉亜さんのための英検準2級合格を目指すAI学習アプリケーション。

---

## 📋 プロジェクト概要

```
対象試験：英検準2級（2026年9月27日）
対象ユーザー：莉亜さん（中2）
目的：英検準2級合格 + オーストラリア留学での実践英語
プラットフォーム：Streamlit Cloud
テクノロジー：Streamlit + Claude API
```

---

## 🎯 学習目標

- 単語：2,600語習得
- ライティング：50-60語エッセイ完成
- スピーキング：オーストラリア留学での実践
- 合格ライン：60点以上（9月27日本番）

---

## 🚀 クイックスタート

### ローカル環境でのセットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/rebale-minobe/GAVI.git
cd GAVI

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. .streamlit/secrets.toml を作成
# .streamlit/ ディレクトリ配下に secrets.toml を作成
# 以下の内容を追加：
# [anthropic]
# api_key = "sk-ant-xxxxx"  # あなたの Claude API Key

# 4. アプリを起動
streamlit run app.py

# ブラウザで http://localhost:8501 を開く
```

---

## 🌐 Streamlit Cloud へのデプロイ

### 初回デプロイ（大志さん用）

```bash
# 1. GitHub にプッシュ
git add -A
git commit -m "feat: GAVI MVP v1.0"
git push origin main

# 2. Streamlit Cloud ダッシュボードにアクセス
https://share.streamlit.io/

# 3. 「New app」をクリック
# Repository: rebale-minobe/GAVI
# Branch: main
# Main file path: app.py

# 4. 「Deploy」をクリック

# 5. デプロイ完了後、以下のURL でアクセス可能
https://gavi-minobe.streamlit.app
```

### Secrets 設定（Streamlit Cloud）

```
1. Streamlit Cloud ダッシュボードで GAVI を選択
2. 「Settings」→「Secrets」
3. 以下を追加：

[anthropic]
api_key = "sk-ant-xxxxx"
```

---

## 📁 ディレクトリ構造

```
GAVI/
├── app.py                    # メインアプリケーション
├── requirements.txt          # Python 依存パッケージ
├── .streamlit/
│   ├── config.toml          # Streamlit 設定
│   └── secrets.toml         # API キー（ローカルのみ）
├── data/
│   ├── words.json           # 単語データベース（2600語）
│   ├── writing_records.json # ライティング記録
│   └── progress.json        # 学習進捗
├── utils/
│   ├── claude_api.py        # Claude API ラッパー
│   └── data_manager.py      # データ管理モジュール
├── assets/
│   └── gavi_logo.svg        # GAVI ロゴ（将来実装）
└── README.md                # このファイル
```

---

## 🔧 技術スタック

| 層 | テクノロジー | 説明 |
|---|---|---|
| **フロントエンド** | Streamlit | シンプルで高速な UI フレームワーク |
| **バックエンド** | Python | データ処理、API 統合 |
| **AI エンジン** | Claude API（Sonnet 4.6） | ライティング採点、会話機能 |
| **データベース** | JSON on GitHub | シンプルで永続的なデータ管理 |
| **デプロイ** | Streamlit Cloud | ワンクリックデプロイ |

---

## 📚 主要機能（MVP）

### Phase 1: 基礎固め期（6月30日リリース）

```
✅ ホーム画面
   - Phase 進捗表示
   - カウントダウン（71日）
   - メインメニュー

✅ 単語学習 4ステップ
   ├─ Step 1: 意味・発音インプット
   ├─ Step 2: 4択クイズ
   ├─ Step 3: 英→日訳（AI採点）
   └─ Step 4: 不正解リスト自動化

✅ データベース
   ├─ words.json（100語デモ）
   ├─ progress.json
   └─ writing_records.json
```

### Phase 2: ライティング実装（7月27日）

```
🚀 ライティング 2モード
   ├─ Free Writing（速度重視）
   └─ Polishing（品質重視）

🚀 iPad Apple Pencil 対応
   ├─ Canvas API 統合
   └─ Claude Vision API で OCR
```

### Phase 3: 本番対策（8月10日）

```
🚀 AI フリートーク
🚀 面接シミュレーション
🚀 Analytics ダッシュボード
```

---

## 🔄 開発進捗

### Week 1-2（6月30日完了 ✅）

- [x] GitHub リポジトリ立ち上げ
- [x] Streamlit 基本構造
- [x] Claude API ラッパー実装
- [x] データ管理モジュール
- [x] ホーム画面実装
- [x] 単語学習 Step 1-2-3
- [x] Streamlit Cloud デプロイ
- [x] MVP テスト

### Week 3-4（7月27日）

- [ ] 単語学習 Step 4（不正解リスト）
- [ ] ライティング Canvas 実装
- [ ] Free Writing 採点ロジック
- [ ] ベータテスト + フィードバック反映

### Week 5-6（8月10日）

- [ ] Polishing モード実装
- [ ] AI フリートーク
- [ ] 面接シミュレーション
- [ ] Analytics ダッシュボード
- [ ] 本番リリース

### Week 7-8（8月24日）

- [ ] バグ修正
- [ ] UI 改善
- [ ] Phase 3 本番対策モード
- [ ] 最終テスト

---

## 🧪 テスト方法

### ローカルテスト

```bash
# 開発モードで起動
streamlit run app.py --logger.level=debug

# テスト：ホーム画面
# → 各メニューボタンが表示されるか確認

# テスト：単語学習
# → Step 1 → Step 2 → Step 3 の流れが正常か確認
```

### Streamlit Cloud テスト

```bash
# デプロイ後、以下で確認
https://gavi-minobe.streamlit.app

# 莉亜さんが実際に使ってみて動作確認
```

---

## 🐛 既知の制限事項（MVP）

```
- 音声機能：Phase 2 で実装予定
- ライティング Canvas：Phase 2 で実装予定
- 面接シミュレーション：Phase 3 で実装予定
- 単語数：デモ版は 100語（最終版は 2,600語）
```

---

## 📊 API 使用量

```
Claude API（claude-sonnet-4-6）
- 単語訳判定：1回 / 単語
- ライティング採点：1回 / 提出
- フリートーク：1回 / メッセージ

月間コスト目安：¥500-1,000（使用量に応じて変動）
```

---

## 👥 開発チーム

| 役割 | 担当 |
|---|---|
| **プロダクトディレクション** | 大志さん（見延博志） |
| **実装 / 開発** | Lémino（AI Assistant） |
| **ユーザーテスト** | 莉亜さん（中2） |

---

## 📞 サポート

### 問題が発生した場合

```
1. GitHub Issues で報告
2. ローカルログを確認
   streamlit run app.py --logger.level=debug
3. Streamlit Cloud のログを確認
   https://share.streamlit.io/ → Settings → Logs
```

### よくある問題

**Q: API Key が見つからないエラー**
```
A: .streamlit/secrets.toml が存在し、
   [anthropic]
   api_key = "sk-ant-xxxxx"
   が記載されているか確認してください。
```

**Q: Streamlit が起動しない**
```
A: pip install -r requirements.txt で依存パッケージを
   再インストールしてください。
```

---

## 📈 学習目標トラッキング

```
進捗ダッシュボード：
https://gavi-minobe.streamlit.app

毎週日曜 18:00 に進捗レポート送付予定
```

---

## 📝 ライセンス

このプロジェクトは莉亜さんのための個人学習ツールです。
著作権は見延家に属します。

---

## 🎯 最終ビジョン

```
2026年9月27日

英検準2級 合格発表

「GAVI のおかげで、毎日楽しく勉強できました。
 オーストラリアでも GAVI がいてくれて
 心強かったです。ありがとう。」

　— 莉亜さん
```

---

**最終更新：** 2026年6月19日  
**バージョン：** MVP 1.0  
**ステータス：** 🚀 デプロイ準備完了

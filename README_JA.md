# 🔐 パスワードジェネレーター

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Web%20%7C%20Windows%20%7C%20macOS%20%7C%20Linux-brightgreen.svg" alt="Platform">
</p>

<p align="center">
  <b>🌐 言語 / Languages:</b><br>
  <a href="README.md">简体中文</a> |
  <a href="README_EN.md">English</a> |
  <a href="README_JA.md">日本語</a> |
  <a href="README_AR.md">العربية</a>
</p>

<p align="center">
  強力で安全なパスワード生成ツール<br>
  Web、Windows、macOS、Linux対応、統一された美しいGUIインターフェース
</p>

---

## 🌐 オンラインで使う

**ダウンロード不要、ブラウザで直接使用可能：**

### 👉 https://zhuyikai2002.github.io/password-generator/

---

## ✨ 機能

| 機能 | 説明 |
|------|------|
| 🔢 **長さ設定** | **8〜128文字**のパスワード長をサポート |
| 📊 **強度評価** | リアルタイムでエントロピー計算と解読時間を推定 |
| 🎯 **文字タイプ** | 大文字、小文字、数字、特殊文字を選択可能 |
| 🚫 **紛らわしい文字を除外** | 紛らわしい文字（0O1lI\|）を除外するオプション |
| 📋 **ワンクリックコピー** | クリップボードに即座にコピー |
| 📜 **履歴** | 生成履歴をローカルに保存、個別削除可能 |
| 📥 **エクスポート** | **TXT / JSON / CSV / Markdown** 形式でダウンロード |
| 🎨 **統一GUI** | すべてのプラットフォームで美しいGUIインターフェース |
| 🔒 **セキュアな乱数** | 暗号学的に安全な乱数生成 |

---

## 📦 ダウンロードとインストール

### オプション1：オンラインで使用（推奨）

https://zhuyikai2002.github.io/password-generator/ にアクセス

### オプション2：クライアントをダウンロード

[Releases ページ](https://github.com/zhuyikai2002/password-generator/releases)からダウンロード：

| ファイル | プラットフォーム | サイズ | 説明 |
|----------|------------------|--------|------|
| `PasswordGenerator-2.0.0-Setup.exe` | Windows | ~1.9MB | 🟢 **インストーラー（推奨）デスクトップショートカット対応** |
| `PasswordGenerator-2.0.0-macOS.dmg` | macOS | ~321KB | 🍎 **ネイティブウィンドウアプリ、直接開く** |
| `PasswordGenerator-2.0.0-Windows-GUI.zip` | Windows | ~10KB | ポータブル版 (ZIP) |
| `pwgen-win.exe` | Windows | ~36MB | コマンドラインバージョン |
| `pwgen` | macOS | ~103KB | CLIツール（Swift） |
| `pwgen-linux` | Linux | ~44MB | CLIツール |

---

## 🚀 クイックスタート

### Windows ユーザー（インストーラー推奨）

1. `PasswordGenerator-2.0.0-Setup.exe` をダウンロード
2. ダブルクリックでインストーラーを実行
3. インストール先を選択、✅「デスクトップショートカットを作成」にチェック
4. インストール完了後、デスクトップアイコンをダブルクリックで実行！

> 💡 またはZIPポータブル版をダウンロードし、解凍して `PasswordGenerator.hta` をダブルクリック

### macOS ユーザー

**GUIアプリケーション：**
1. `PasswordGenerator-2.0.0-macOS.dmg` をダウンロード
2. DMGを開き、アプリをApplicationsにドラッグ
3. ダブルクリックで実行、**ネイティブウィンドウが直接開きます（ブラウザ不要）！**

**コマンドライン：**
```bash
chmod +x pwgen
./pwgen
```

### Linux ユーザー

```bash
chmod +x pwgen-linux
./pwgen-linux
```

またはオンラインバージョンを直接使用！

---

## 📥 履歴エクスポート機能

生成されたパスワードは自動的にローカル履歴に保存されます。複数の形式でエクスポート可能：

| 形式 | 説明 |
|------|------|
| 📄 **TXT** | プレーンテキスト、1行に1パスワード |
| 📋 **JSON** | パスワード、長さ、エントロピーを含む構造化データ |
| 📊 **CSV** | テーブル形式、Excelで開ける |
| 📝 **Markdown** | フォーマットされたテーブル、ドキュメント向け |

**使い方：**
1. 履歴セクションの「⬇️ ダウンロード」ボタンをクリック
2. 希望の形式を選択
3. 確認してダウンロード

---

## 📖 CLI 使用ガイド

### 基本的な使い方

```bash
# インタラクティブモード（初心者向け）
pwgen

# 指定した長さのパスワードを生成（8-128）
pwgen -l 16
pwgen -l 128    # 最大128文字

# 複数のパスワードを一括生成
pwgen -l 20 -c 5 -b

# 紛らわしい文字を除外
pwgen -l 16 -e
```

### すべてのパラメータ

| パラメータ | 完全形式 | 説明 | デフォルト |
|------------|----------|------|------------|
| `-l` | `--length` | パスワードの長さ (8-128) | 12 |
| `-c` | `--count` | 生成数 | 3 |
| `-e` | `--exclude` | 紛らわしい文字を除外 | いいえ |
| `-b` | `--batch` | バッチモード | いいえ |
| | `--no-upper` | 大文字なし | いいえ |
| | `--no-lower` | 小文字なし | いいえ |
| | `--no-digits` | 数字なし | いいえ |
| | `--no-special` | 特殊文字なし | いいえ |
| | `--json` | JSON形式で出力 | いいえ |
| | `--plain` | プレーンテキスト出力 | いいえ |
| `-h` | `--help` | ヘルプを表示 | - |

---

## 🔒 パスワード強度レベル

| レベル | アイコン | エントロピー (bits) | 推定解読時間 |
|--------|----------|---------------------|--------------|
| 非常に弱い | 🔴 | < 28 | 瞬時 |
| 弱い | 🟠 | 28-36 | 数時間 |
| 中程度 | 🟡 | 36-60 | 数日〜数ヶ月 |
| 強い | 🟢 | 60-80 | 数年〜数百年 |
| 非常に強い | 🔵 | 80-100 | 数千年 |
| 極めて強い | 🟣 | > 100 | 宇宙の年齢レベル |

> 💡 **推奨事項:** 重要なアカウントには16文字以上、エントロピー80以上のパスワードを使用してください

---

## 🏗️ 技術アーキテクチャ

このプロジェクトは複数の言語で実装されており、異なるプラットフォームに対応しています：

```
password-generator/
├── docs/                    # Web版（GitHub Pages）
│   └── index.html
├── app/                     # デスクトップアプリケーション
│   ├── PasswordGenerator.hta    # Windows GUI (HTA)
│   ├── pwgen.html              # 共通HTMLインターフェース
│   └── 启动密码生成器.bat
├── generate-password.py     # Python版
├── generate-password.js     # Node.js版
├── generate-password.swift  # Swift版
└── dist/                    # ビルド出力
```

### セキュリティについて

- **Web版**: `crypto.getRandomValues()` Web Crypto API を使用
- **Python版**: `secrets` モジュール（暗号学的に安全）を使用
- **Swift版**: システムレベルのセキュア乱数を使用
- **Node.js版**: `crypto.randomInt()` を使用

すべてのバージョンで暗号学的に安全な乱数生成器を使用し、十分なランダム性を確保しています。

---

## 🤝 コントリビューション

Issue や Pull Request を歓迎します！

1. このリポジトリをフォーク
2. 機能ブランチを作成（`git checkout -b feature/amazing-feature`）
3. 変更をコミット（`git commit -m 'Add amazing feature'`）
4. ブランチをプッシュ（`git push origin feature/amazing-feature`）
5. Pull Request を作成

---

## 📄 ライセンス

このプロジェクトは [MIT ライセンス](LICENSE)の下で公開されています。

---

<p align="center">
  このプロジェクトが役立ったら、⭐ スターをお願いします！
</p>

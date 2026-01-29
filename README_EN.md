# 🔐 Password Generator

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Web%20%7C%20Windows%20%7C%20macOS%20%7C%20Linux-brightgreen.svg" alt="Platform">
</p>

<p align="center">
  <b>🌐 Languages:</b><br>
  <a href="README.md">简体中文</a> |
  <a href="README_EN.md">English</a> |
  <a href="README_JA.md">日本語</a> |
  <a href="README_AR.md">العربية</a>
</p>

<p align="center">
  A powerful and secure password generation tool<br>
  Supporting Web, Windows, macOS, and Linux with unified beautiful GUI
</p>

---

## 🌐 Online Demo

**No download required, use it directly in your browser:**

### 👉 https://zhuyikai2002.github.io/password-generator/

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔢 **Configurable Length** | Support **8-128** character password length |
| 📊 **Strength Assessment** | Real-time entropy calculation and crack time estimation |
| 🎯 **Character Types** | Choose from uppercase, lowercase, numbers, symbols |
| 🚫 **Exclude Ambiguous** | Option to exclude confusing characters (0O1lI\|) |
| 📋 **One-Click Copy** | Copy to clipboard instantly |
| 📜 **History** | Local storage for generated passwords with delete option |
| 📥 **Export Download** | Export as **TXT / JSON / CSV / Markdown** formats |
| 🎨 **Unified GUI** | Beautiful GUI interface across all platforms |
| 🔒 **Secure Random** | Cryptographically secure random number generation |

---

## 📦 Download & Install

### Option 1: Use Online (Recommended)

Visit https://zhuyikai2002.github.io/password-generator/

### Option 2: Download Client

Go to [Releases Page](https://github.com/zhuyikai2002/password-generator/releases) to download:

| File | Platform | Size | Description |
|------|----------|------|-------------|
| `PasswordGenerator-2.0.0-Windows-GUI.zip` | Windows | ~10KB | 🟢 **GUI version, double-click to run** |
| `PasswordGenerator-2.0.0-macOS.dmg` | macOS | ~340KB | 🍎 GUI application (with icon) |
| `pwgen-win.exe` | Windows | ~36MB | Command line version |
| `pwgen` | macOS | ~103KB | CLI tool (Swift) |
| `pwgen-linux` | Linux | ~44MB | CLI tool |

---

## 🚀 Quick Start

### Windows Users (GUI Recommended)

1. Download `PasswordGenerator-2.0.0-Windows-GUI.zip`
2. Extract and double-click `PasswordGenerator.hta`
3. Enjoy the beautiful graphical interface!

> 💡 You can also double-click `启动密码生成器.bat` to run

### macOS Users

**GUI Application:**
1. Download `PasswordGenerator-2.0.0-macOS.dmg`
2. Open DMG, drag the app to Applications
3. Double-click to run, opens in browser with beautiful interface

**Command Line:**
```bash
chmod +x pwgen
./pwgen
```

### Linux Users

```bash
chmod +x pwgen-linux
./pwgen-linux
```

Or use the online version directly!

---

## 📥 History Export Feature

Generated passwords are automatically saved to local history. Export in multiple formats:

| Format | Description |
|--------|-------------|
| 📄 **TXT** | Plain text, one password per line |
| 📋 **JSON** | Structured data with password, length, entropy |
| 📊 **CSV** | Table format, compatible with Excel |
| 📝 **Markdown** | Formatted table for documentation |

**How to use:**
1. Click the "⬇️ Download" button in the history section
2. Select desired format
3. Confirm to download

---

## 📖 CLI Usage Guide

### Basic Usage

```bash
# Interactive mode (recommended for beginners)
pwgen

# Generate password with specific length (8-128)
pwgen -l 16
pwgen -l 128    # Maximum 128 characters

# Batch generate multiple passwords
pwgen -l 20 -c 5 -b

# Exclude ambiguous characters
pwgen -l 16 -e
```

### All Parameters

| Param | Full Form | Description | Default |
|-------|-----------|-------------|---------|
| `-l` | `--length` | Password length (8-128) | 12 |
| `-c` | `--count` | Number to generate | 3 |
| `-e` | `--exclude` | Exclude ambiguous chars | No |
| `-b` | `--batch` | Batch mode | No |
| | `--no-upper` | No uppercase letters | No |
| | `--no-lower` | No lowercase letters | No |
| | `--no-digits` | No numbers | No |
| | `--no-special` | No special characters | No |
| | `--json` | JSON output format | No |
| | `--plain` | Plain text output | No |
| `-h` | `--help` | Show help | - |

---

## 🔒 Password Strength Levels

| Level | Icon | Entropy (bits) | Estimated Crack Time |
|-------|------|----------------|----------------------|
| Very Weak | 🔴 | < 28 | Instant |
| Weak | 🟠 | 28-36 | Hours |
| Medium | 🟡 | 36-60 | Days to months |
| Strong | 🟢 | 60-80 | Years to centuries |
| Very Strong | 🔵 | 80-100 | Thousands of years |
| Extremely Strong | 🟣 | > 100 | Age of universe |

> 💡 **Recommendation:** Use 16+ characters with 80+ entropy for important accounts

---

## 🏗️ Technical Architecture

This project is implemented in multiple languages for different platforms:

```
password-generator/
├── docs/                    # Web version (GitHub Pages)
│   └── index.html
├── app/                     # Desktop applications
│   ├── PasswordGenerator.hta    # Windows GUI (HTA)
│   ├── pwgen.html              # Universal HTML interface
│   └── 启动密码生成器.bat
├── generate-password.py     # Python version
├── generate-password.js     # Node.js version
├── generate-password.swift  # Swift version
└── dist/                    # Build output
```

### Security Notes

- **Web version**: Uses `crypto.getRandomValues()` Web Crypto API
- **Python version**: Uses `secrets` module (cryptographically secure)
- **Swift version**: Uses system-level secure random
- **Node.js version**: Uses `crypto.randomInt()`

All versions use cryptographically secure random number generators to ensure sufficient randomness.

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork this repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  If this project helps you, please give it a ⭐ Star!
</p>

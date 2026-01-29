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
  Supporting Web, Windows, macOS, and Linux
</p>

---

## 🌐 Online Demo

**No download required, use it directly in your browser:**

### 👉 https://zhuyikai2002.github.io/password-generator/

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔢 **Configurable Length** | Support 8-128 character password length |
| 📊 **Strength Assessment** | Real-time entropy calculation and crack time estimation |
| 🎯 **Character Types** | Choose from uppercase, lowercase, numbers, symbols |
| 🚫 **Exclude Ambiguous** | Option to exclude confusing characters (0O1lI\|) |
| 📋 **One-Click Copy** | Copy to clipboard instantly |
| 📁 **Multiple Formats** | Interactive, JSON, and plain text output |
| 🔒 **Secure Random** | Cryptographically secure random number generation |
| 📜 **History** | Local storage for generated passwords (Web version) |

---

## 📦 Download & Install

### Option 1: Use Online (Recommended)

Visit https://zhuyikai2002.github.io/password-generator/

### Option 2: Download Client

Go to [Releases Page](https://github.com/zhuyikai2002/password-generator/releases) to download:

| File | Platform | Size | Description |
|------|----------|------|-------------|
| `pwgen-win.exe` | Windows | ~36MB | 🟢 Portable, double-click to run |
| `PasswordGenerator-2.0.0-macOS.dmg` | macOS | ~334KB | Application (with icon) |
| `pwgen` | macOS | ~103KB | CLI tool (Swift) |
| `pwgen-linux` | Linux | ~44MB | CLI tool |

---

## 🚀 Quick Start

### Windows Users

1. Download `pwgen-win.exe`
2. Double-click to run, no installation required
3. If blocked by security software, click "More info" → "Run anyway"

### macOS Users

**GUI Application:**
1. Download `PasswordGenerator-2.0.0-macOS.dmg`
2. Open DMG, drag the app to Applications
3. Double-click to run

**Command Line:**
```bash
# Download and add execute permission
chmod +x pwgen

# Run
./pwgen

# Global install (optional)
sudo cp pwgen /usr/local/bin/
```

### Linux Users

```bash
# Download and add execute permission
chmod +x pwgen-linux

# Run
./pwgen-linux
```

---

## 📖 CLI Usage Guide

### Basic Usage

```bash
# Interactive mode (recommended for beginners)
pwgen

# Generate password with specific length
pwgen -l 16

# Batch generate multiple passwords
pwgen -l 20 -c 5 -b

# Exclude ambiguous characters
pwgen -l 16 -e
```

### All Parameters

| Param | Full Form | Description | Default |
|-------|-----------|-------------|---------|
| `-l` | `--length` | Password length | 12 |
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

### Output Format Examples

**Interactive Mode:**
```
╔══════════════════════════════════════════════════════════╗
║                 Password Generator v2.0                   ║
╚══════════════════════════════════════════════════════════╝

Generated passwords:

  [1] Kx9#mPq$Lw2@
      🟣 Strength: Very Strong | Entropy: 78.66 bits | Crack time: Millions of years

Commands: [1-3] Select | [r] Regenerate | [l] Change length | [q] Quit
```

**JSON Format:**
```json
{
  "generated_at": "2024-01-29T12:00:00Z",
  "passwords": [
    {
      "password": "Kx9#mPq$Lw2@",
      "entropy": 78.66,
      "strength": "Very Strong"
    }
  ]
}
```

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
├── docs/                    # Web version (HTML/CSS/JS)
│   └── index.html
├── generate-password.py     # Python version (most features)
├── generate-password.js     # Node.js version (cross-platform)
├── generate-password.swift  # Swift version (macOS native)
├── pwgen                    # Swift compiled binary
└── dist/                    # Build output
    ├── pwgen-win.exe        # Windows executable
    ├── pwgen-linux          # Linux executable
    └── pwgen-node           # Node.js packaged version
```

### Security Notes

- **Web version**: Uses `crypto.getRandomValues()` Web Crypto API
- **Python version**: Uses `secrets` module (cryptographically secure)
- **Swift version**: Uses system-level secure random
- **Node.js version**: Uses `crypto.randomInt()`

All versions use cryptographically secure random number generators to ensure sufficient randomness.

---

## 🛠️ Local Development

### Clone Repository

```bash
git clone https://github.com/zhuyikai2002/password-generator.git
cd password-generator
```

### Run Different Versions

```bash
# Python version
python3 generate-password.py

# Node.js version
node generate-password.js

# Swift version (requires macOS)
swift generate-password.swift
# Or compile and run
swiftc -O -o pwgen generate-password.swift
./pwgen
```

### Build & Package

```bash
# Package for Windows
npx pkg generate-password.js -t node18-win-x64 -o dist/pwgen-win.exe

# Package for Linux
npx pkg generate-password.js -t node18-linux-x64 -o dist/pwgen-linux

# Package for macOS (Node.js)
npx pkg generate-password.js -t node18-macos-arm64 -o dist/pwgen-node

# Compile Swift (macOS)
swiftc -O -o pwgen generate-password.swift
```

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

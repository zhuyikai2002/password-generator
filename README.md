# 🔐 强密码生成器 | Password Generator

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Web%20%7C%20Windows%20%7C%20macOS%20%7C%20Linux-brightgreen.svg" alt="Platform">
</p>

<p align="center">
  <b>🌐 语言 / Languages:</b><br>
  <a href="README.md">简体中文</a> |
  <a href="README_EN.md">English</a> |
  <a href="README_JA.md">日本語</a> |
  <a href="README_AR.md">العربية</a>
</p>

<p align="center">
  一个功能强大、安全可靠的密码生成工具<br>
  支持 Web、Windows、macOS、Linux 全平台，统一美观的 GUI 界面
</p>

---

## 🌐 在线使用

**无需下载，打开浏览器即可使用：**

### 👉 https://zhuyikai2002.github.io/password-generator/

---

## ✨ 功能特性

| 功能 | 描述 |
|------|------|
| 🔢 **可配置长度** | 支持 **8-128 位**密码长度自由调整 |
| 📊 **强度评估** | 实时计算密码熵值，估算暴力破解所需时间 |
| 🎯 **字符类型** | 可选择大写字母、小写字母、数字、特殊字符 |
| 🚫 **排除混淆** | 可排除易混淆字符 (0O1lI\|) |
| 📋 **一键复制** | 点击即可复制到剪贴板 |
| 📜 **历史记录** | 本地保存生成历史，支持单条删除 |
| 📥 **下载导出** | 支持导出为 **TXT / JSON / CSV / Markdown** 四种格式 |
| 🎨 **统一界面** | 全平台统一美观的 GUI 界面 |
| 🔒 **安全随机** | 使用密码学安全的随机数生成器 |

---

## 📦 下载安装

### 方式一：在线使用（推荐）

直接访问 https://zhuyikai2002.github.io/password-generator/

### 方式二：下载客户端

前往 [Releases 页面](https://github.com/zhuyikai2002/password-generator/releases) 下载：

| 文件 | 平台 | 大小 | 说明 |
|------|------|------|------|
| `PasswordGenerator-2.0.0-Windows-GUI.zip` | Windows | ~10KB | 🟢 **GUI 版本，双击运行，美观界面** |
| `PasswordGenerator-2.0.0-macOS.dmg` | macOS | ~340KB | 🍎 GUI 应用（带图标） |
| `pwgen-win.exe` | Windows | ~36MB | 命令行版本 |
| `pwgen` | macOS | ~103KB | 命令行工具 (Swift) |
| `pwgen-linux` | Linux | ~44MB | 命令行工具 |

---

## 🚀 快速开始

### Windows 用户（推荐 GUI 版）

1. 下载 `PasswordGenerator-2.0.0-Windows-GUI.zip`
2. 解压后双击 `PasswordGenerator.hta`
3. 享受美观的图形界面！

> 💡 也可以双击 `启动密码生成器.bat` 运行

### macOS 用户

**图形界面：**
1. 下载 `PasswordGenerator-2.0.0-macOS.dmg`
2. 打开 DMG，将应用拖拽到 Applications
3. 双击运行，在浏览器中打开美观界面

**命令行：**
```bash
chmod +x pwgen
./pwgen
```

### Linux 用户

```bash
chmod +x pwgen-linux
./pwgen-linux
```

或直接使用在线版本！

---

## 📥 历史记录下载功能

生成的密码会自动保存到本地历史记录，支持导出为多种格式：

| 格式 | 说明 |
|------|------|
| 📄 **TXT** | 纯文本格式，每行一个密码 |
| 📋 **JSON** | 结构化数据，包含密码、长度、熵值信息 |
| 📊 **CSV** | 表格格式，可用 Excel 打开 |
| 📝 **Markdown** | 带格式的表格，适合文档 |

**使用方法：**
1. 点击历史记录区域的「⬇️ 下载」按钮
2. 选择需要的格式
3. 确认后自动下载到本地

---

## 📖 命令行使用指南

### 基本用法

```bash
# 交互模式（推荐新手）
pwgen

# 生成指定长度的密码（支持 8-128 位）
pwgen -l 16
pwgen -l 128    # 最长支持 128 位

# 批量生成多个密码
pwgen -l 20 -c 5 -b

# 排除易混淆字符
pwgen -l 16 -e
```

### 所有参数

| 参数 | 完整形式 | 说明 | 默认值 |
|------|----------|------|--------|
| `-l` | `--length` | 密码长度 (8-128) | 12 |
| `-c` | `--count` | 生成数量 | 3 |
| `-e` | `--exclude` | 排除混淆字符 | 否 |
| `-b` | `--batch` | 批量模式 | 否 |
| | `--no-upper` | 不含大写字母 | 否 |
| | `--no-lower` | 不含小写字母 | 否 |
| | `--no-digits` | 不含数字 | 否 |
| | `--no-special` | 不含特殊字符 | 否 |
| | `--json` | JSON 格式输出 | 否 |
| | `--plain` | 纯文本输出 | 否 |
| `-h` | `--help` | 显示帮助 | - |

---

## 🔒 密码强度说明

| 等级 | 图标 | 熵值 (bits) | 破解时间估算 |
|------|------|-------------|--------------|
| 极弱 | 🔴 | < 28 | 瞬间 |
| 弱 | 🟠 | 28-36 | 数小时 |
| 中等 | 🟡 | 36-60 | 数天至数月 |
| 强 | 🟢 | 60-80 | 数年至数百年 |
| 很强 | 🔵 | 80-100 | 数千年 |
| 极强 | 🟣 | > 100 | 宇宙年龄级别 |

> 💡 **建议：** 重要账户请使用 16 位以上、熵值 80+ 的密码

---

## 🏗️ 技术架构

本项目采用多语言实现，适应不同平台和场景：

```
password-generator/
├── docs/                    # Web 版本 (GitHub Pages)
│   └── index.html
├── app/                     # 桌面应用
│   ├── PasswordGenerator.hta    # Windows GUI (HTA)
│   ├── pwgen.html              # 通用 HTML 界面
│   └── 启动密码生成器.bat
├── generate-password.py     # Python 版本
├── generate-password.js     # Node.js 版本
├── generate-password.swift  # Swift 版本
└── dist/                    # 打包输出
```

### 安全性说明

- **Web 版本**: 使用 `crypto.getRandomValues()` Web Crypto API
- **Python 版本**: 使用 `secrets` 模块（密码学安全）
- **Swift 版本**: 使用系统级安全随机数
- **Node.js 版本**: 使用 `crypto.randomInt()`

所有版本均使用密码学安全的随机数生成器，确保生成的密码具有足够的随机性。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 开源协议

本项目采用 [MIT 协议](LICENSE) 开源。

---

<p align="center">
  如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！
</p>

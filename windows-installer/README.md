# Windows 安装程序构建指南

本目录包含创建 Windows 安装程序所需的文件。

## 文件说明

```
windows-installer/
├── setup.iss          # Inno Setup 脚本
├── files/
│   ├── PasswordGenerator.hta   # 主程序
│   ├── pwgen.html              # HTML 界面
│   └── icon.ico                # 图标文件
└── output/
    └── PasswordGenerator-2.0.0-Setup.exe  # 生成的安装程序
```

## 构建步骤

### 1. 安装 Inno Setup

下载并安装 Inno Setup 6.x：
https://jrsoftware.org/isdl.php

### 2. 准备文件

确保 `files/` 目录包含以下文件：
- `PasswordGenerator.hta` - 从 `app/` 目录复制
- `pwgen.html` - 从 `app/` 目录复制
- `icon.ico` - 应用图标

### 3. 编译安装程序

方法一：双击 `setup.iss` 文件，Inno Setup 会自动打开，点击 "Build" -> "Compile"

方法二：命令行编译
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

### 4. 获取安装程序

编译完成后，安装程序位于：
```
output/PasswordGenerator-2.0.0-Setup.exe
```

## 安装程序功能

- ✅ 自定义安装目录
- ✅ 创建桌面快捷方式（可选）
- ✅ 创建开始菜单快捷方式
- ✅ 安装完成后可选立即运行
- ✅ 支持卸载
- ✅ 中英文双语界面

## 快速构建（已有 Inno Setup）

```powershell
# 复制文件到 files 目录
mkdir files -Force
Copy-Item ..\app\PasswordGenerator.hta files\
Copy-Item ..\app\pwgen.html files\

# 编译
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

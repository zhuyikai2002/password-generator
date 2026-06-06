#!/usr/bin/env python3
"""
passgen 自动化构建脚本
使用 PyInstaller 将密码生成器打包为单文件可执行程序。

用法:
    python build_app.py

构建产物:
    ./bin/passgen.exe  (Windows)
    ./bin/passgen      (Linux/macOS)

注意:
    - 需要先安装 PyInstaller: pip install pyinstaller
    - .env 配置文件请放在与可执行文件同级目录
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


# ==================== 构建配置 ====================

# 输出可执行文件名（不含扩展名）
APP_NAME = "passgen"

# 入口脚本
ENTRY_SCRIPT = "generate-password.py"

# 构建输出目录
BIN_DIR = Path("bin")

# PyInstaller 可能漏掉的隐式依赖
HIDDEN_IMPORTS = [
    # cryptography 底层模块
    "cryptography",
    "cryptography.fernet",
    "cryptography.hazmat.primitives",
    "cryptography.hazmat.primitives.kdf.pbkdf2",
    "cryptography.hazmat.primitives.hashes",
    "cryptography.hazmat.primitives.ciphers",
    "cryptography.hazmat.primitives.ciphers.algorithms",
    "cryptography.hazmat.primitives.ciphers.modes",
    "cryptography.hazmat.backends",
    "cryptography.hazmat.backends.openssl",
    "cryptography.hazmat.backends.openssl.backend",
    "cryptography.hazmat.bindings._rust",
    # paramiko SSH/SFTP
    "paramiko",
    "paramiko.transport",
    "paramiko.sftp_client",
    "paramiko.rsakey",
    "paramiko.ecdsakey",
    "paramiko.ed25519key",
    "paramiko.dsskey",
    "paramiko.ssh_exception",
    "bcrypt",
    "nacl",
    "nacl.bindings",
    # dotenv
    "dotenv",
    # rich TUI
    "rich",
    "rich.console",
    "rich.panel",
    "rich.table",
    "rich.text",
    "rich.prompt",
    "rich.box",
    "rich.markup",
    "rich.highlighter",
    "rich.themes",
    # 标准库中 PyInstaller 偶尔漏掉的
    "getpass",
    "hashlib",
    "secrets",
]

# PyInstaller 产生的临时文件/目录
CLEANUP_TARGETS = ["build", "dist", f"{APP_NAME}.spec"]


# ==================== 构建逻辑 ====================

def check_prerequisites():
    """检查构建前提条件"""
    print("=" * 60)
    print(f"  passgen 构建脚本")
    print(f"  平台: {platform.system()} {platform.machine()}")
    print(f"  Python: {sys.version.split()[0]}")
    print("=" * 60)
    print()

    # 检查入口脚本
    if not Path(ENTRY_SCRIPT).exists():
        print(f"[错误] 入口脚本 {ENTRY_SCRIPT} 不存在！")
        print(f"       请在项目根目录运行此脚本。")
        sys.exit(1)

    # 检查 PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller 未安装！")
        print("  请运行: pip install pyinstaller")
        sys.exit(1)

    # 检查核心依赖
    deps = {
        "cryptography": "cryptography",
        "paramiko": "paramiko",
        "dotenv": "python-dotenv",
        "rich": "rich",
    }
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} 未安装！")
            print(f"  请运行: pip install {package}")
            sys.exit(1)

    print()


def build():
    """执行 PyInstaller 构建"""
    print("🔨 开始构建...\n")

    # 构建命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # 单文件输出
        "--console",           # 保留控制台（TUI 必须）
        f"--name={APP_NAME}",  # 可执行文件名
        "--clean",             # 清理缓存后重新构建
        "--noconfirm",         # 覆盖已有输出不询问
    ]

    # 添加隐式依赖
    for module in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", module])

    # 入口脚本
    cmd.append(ENTRY_SCRIPT)

    print(f"  命令: {' '.join(cmd[:6])} ... {cmd[-1]}")
    print(f"  隐式依赖: {len(HIDDEN_IMPORTS)} 个模块")
    print()

    # 执行构建
    result = subprocess.run(cmd, cwd=str(Path.cwd()))

    if result.returncode != 0:
        print("\n✗ 构建失败！请检查上方错误信息。")
        sys.exit(1)

    print("\n✓ PyInstaller 构建完成")


def organize_output():
    """整理构建产物到 bin/ 目录"""
    print("\n📦 整理构建产物...\n")

    # 确定可执行文件路径
    if platform.system() == "Windows":
        exe_name = f"{APP_NAME}.exe"
    else:
        exe_name = APP_NAME

    dist_exe = Path("dist") / exe_name

    if not dist_exe.exists():
        print(f"✗ 未找到构建产物: {dist_exe}")
        sys.exit(1)

    # 创建 bin/ 目录
    BIN_DIR.mkdir(exist_ok=True)

    # 移动可执行文件
    target = BIN_DIR / exe_name
    if target.exists():
        target.unlink()
    shutil.move(str(dist_exe), str(target))

    file_size_mb = target.stat().st_size / (1024 * 1024)
    print(f"  ✓ {target}  ({file_size_mb:.1f} MB)")


def cleanup():
    """清理 PyInstaller 临时文件"""
    print("\n🧹 清理临时文件...\n")

    for target in CLEANUP_TARGETS:
        path = Path(target)
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            print(f"  ✓ 已删除目录: {target}/")
        elif path.is_file():
            path.unlink()
            print(f"  ✓ 已删除文件: {target}")

    # 清理 __pycache__
    for cache_dir in Path.cwd().rglob("__pycache__"):
        shutil.rmtree(cache_dir, ignore_errors=True)

    print()


def print_summary():
    """打印构建摘要"""
    if platform.system() == "Windows":
        exe_path = BIN_DIR / f"{APP_NAME}.exe"
        run_cmd = f".\\bin\\{APP_NAME}.exe"
    else:
        exe_path = BIN_DIR / APP_NAME
        run_cmd = f"./bin/{APP_NAME}"

    print("=" * 60)
    print("  ✅ 构建成功！")
    print("=" * 60)
    print()
    print(f"  可执行文件: {exe_path}")
    print(f"  文件大小:   {exe_path.stat().st_size / (1024*1024):.1f} MB")
    print()
    print("  使用方法:")
    print(f"    {run_cmd}                    # 交互模式")
    print(f"    {run_cmd} -b -l 20 -c 5     # 批量生成")
    print(f"    {run_cmd} --read-encrypted   # 解密读取")
    print(f"    {run_cmd} --sync-pull        # 云端拉取")
    print()
    print("  📌 .env 配置文件说明:")
    print(f"     将 .env 文件放在与 {exe_path.name} 同级目录下。")
    print(f"     例如 U 盘里的目录结构:")
    print()
    print(f"     U:\\passgen\\")
    print(f"       ├── {exe_path.name}")
    print(f"       └── .env          # SFTP 配置 (可选)")
    print()
    print("  💡 提示: 直接拷贝到 U 盘即可随插随用！")
    print("=" * 60)


# ==================== 主入口 ====================

def main():
    check_prerequisites()
    build()
    organize_output()
    cleanup()
    print_summary()


if __name__ == "__main__":
    main()

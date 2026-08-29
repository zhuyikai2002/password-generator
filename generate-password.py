#!/usr/bin/env python3
"""
强密码生成器 v2.0
功能：可配置长度、密码强度评估、排除易混淆字符、多种输出格式、密码历史记录
"""

import argparse
import base64
import getpass
import hashlib
import json
import math
import os
import secrets
import socket
import string
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt
from rich import box

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Rich 终端实例
console = Console()


# ==================== 配置 ====================

DEFAULT_LENGTH = 12
DEFAULT_COUNT = 3
MIN_LENGTH = 8
MAX_LENGTH = 128

# 字符集
UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SPECIAL = "!@#$%^&*_+-=[]{}|;:,.<>?"

# 易混淆字符
CONFUSING_CHARS = "0O1lI|"

# 历史记录文件
HISTORY_FILE = Path.home() / ".password_history.json"

# 加密密码存储文件
ENCRYPTED_FILE = Path.home() / ".passwords.enc"
SALT_FILE = Path.home() / ".passwords.salt"

# SFTP 云端同步配置（从环境变量或 .env 文件读取）
SFTP_HOST = os.environ.get("SFTP_HOST", "")
SFTP_PORT = int(os.environ.get("SFTP_PORT", "22"))
SFTP_USER = os.environ.get("SFTP_USER", "")
SFTP_PASSWORD = os.environ.get("SFTP_PASSWORD", "")
SFTP_KEY_PATH = os.environ.get("SFTP_KEY_PATH", "")
REMOTE_DIR = os.environ.get("SFTP_REMOTE_DIR", "/home/user/password-sync")


# ==================== 密码生成 ====================

def get_charset(exclude_confusing: bool = False, 
                include_uppercase: bool = True,
                include_lowercase: bool = True,
                include_digits: bool = True,
                include_special: bool = True) -> dict[str, str]:
    """获取字符集"""
    chars = {
        'uppercase': UPPERCASE if include_uppercase else '',
        'lowercase': LOWERCASE if include_lowercase else '',
        'digits': DIGITS if include_digits else '',
        'special': SPECIAL if include_special else '',
    }
    
    if exclude_confusing:
        for key in chars:
            chars[key] = ''.join(c for c in chars[key] if c not in CONFUSING_CHARS)
    
    return chars


def generate_strong_password(length: int, 
                             exclude_confusing: bool = False,
                             include_uppercase: bool = True,
                             include_lowercase: bool = True,
                             include_digits: bool = True,
                             include_special: bool = True) -> str:
    """生成强密码"""
    chars = get_charset(exclude_confusing, include_uppercase, 
                        include_lowercase, include_digits, include_special)
    
    all_chars = ''.join(chars.values())
    
    if not all_chars:
        raise ValueError("至少需要选择一种字符类型")
    
    # 计算需要的最小字符类型数量
    required_chars = []
    if chars['uppercase']:
        required_chars.append(secrets.choice(chars['uppercase']))
    if chars['lowercase']:
        required_chars.append(secrets.choice(chars['lowercase']))
    if chars['digits']:
        required_chars.append(secrets.choice(chars['digits']))
    if chars['special']:
        required_chars.append(secrets.choice(chars['special']))
    
    # 如果长度小于必需字符数，调整策略
    if length < len(required_chars):
        password = [secrets.choice(all_chars) for _ in range(length)]
    else:
        # 填充剩余字符
        password = required_chars + [secrets.choice(all_chars) for _ in range(length - len(required_chars))]
    
    # 打乱顺序
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


# ==================== 密码强度评估 ====================

def calculate_entropy(password: str) -> float:
    """计算密码熵值（bits）"""
    charset_size = 0
    
    has_upper = any(c in UPPERCASE for c in password)
    has_lower = any(c in LOWERCASE for c in password)
    has_digit = any(c in DIGITS for c in password)
    has_special = any(c in SPECIAL for c in password)
    
    if has_upper:
        charset_size += 26
    if has_lower:
        charset_size += 26
    if has_digit:
        charset_size += 10
    if has_special:
        charset_size += len(SPECIAL)
    
    if charset_size == 0:
        return 0
    
    entropy = len(password) * math.log2(charset_size)
    return round(entropy, 2)


def evaluate_strength(entropy: float) -> tuple:
    """评估密码强度"""
    if entropy < 28:
        return ("极弱", "🔴", "容易被暴力破解")
    elif entropy < 36:
        return ("弱", "🟠", "可能在数小时内被破解")
    elif entropy < 60:
        return ("中等", "🟡", "可抵御一般攻击")
    elif entropy < 80:
        return ("强", "🟢", "可抵御大多数攻击")
    elif entropy < 100:
        return ("很强", "🔵", "非常安全")
    else:
        return ("极强", "🟣", "几乎不可能被破解")


def get_crack_time_estimate(entropy: float) -> str:
    """估算破解时间（假设每秒 10^12 次尝试）"""
    attempts_per_second = 1e12  # 1万亿次/秒
    total_combinations = 2 ** entropy
    seconds = total_combinations / attempts_per_second
    
    if seconds < 1:
        return "瞬间"
    elif seconds < 60:
        return f"{seconds:.1f} 秒"
    elif seconds < 3600:
        return f"{seconds/60:.1f} 分钟"
    elif seconds < 86400:
        return f"{seconds/3600:.1f} 小时"
    elif seconds < 31536000:
        return f"{seconds/86400:.1f} 天"
    elif seconds < 31536000 * 100:
        return f"{seconds/31536000:.1f} 年"
    elif seconds < 31536000 * 1e6:
        return f"{seconds/31536000/1000:.1f} 千年"
    elif seconds < 31536000 * 1e9:
        return f"{seconds/31536000/1e6:.1f} 百万年"
    else:
        return "宇宙年龄级别"


def analyze_password(password: str) -> dict:
    """分析密码"""
    entropy = calculate_entropy(password)
    strength, icon, description = evaluate_strength(entropy)
    crack_time = get_crack_time_estimate(entropy)
    
    return {
        "password": password,
        "length": len(password),
        "entropy": entropy,
        "strength": strength,
        "icon": icon,
        "description": description,
        "crack_time": crack_time,
        "has_uppercase": any(c in UPPERCASE for c in password),
        "has_lowercase": any(c in LOWERCASE for c in password),
        "has_digits": any(c in DIGITS for c in password),
        "has_special": any(c in SPECIAL for c in password),
    }


# ==================== 剪贴板 ====================

def copy_to_clipboard(text: str) -> bool:
    """复制到剪贴板"""
    try:
        # macOS
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        process.communicate(text.encode('utf-8'))
        return process.returncode == 0
    except FileNotFoundError:
        try:
            # Linux
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                       stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
            process.communicate(text.encode('utf-8'))
            return process.returncode == 0
        except FileNotFoundError:
            return False


# ==================== 历史记录 ====================

def hash_password(password: str) -> str:
    """对密码进行哈希（不存储明文）"""
    return hashlib.sha256(password.encode()).hexdigest()[:16]


def save_to_history(password: str, metadata: dict | None = None):
    """保存到历史记录（只存储哈希和元数据）"""
    history = load_history()
    
    record = {
        "hash": hash_password(password),
        "length": len(password),
        "entropy": metadata.get("entropy", 0) if metadata else calculate_entropy(password),
        "strength": metadata.get("strength", "") if metadata else "",
        "created_at": datetime.now().isoformat(),
    }
    
    history.append(record)
    
    # 只保留最近 100 条
    history = history[-100:]
    
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # 静默失败


def load_history() -> list:
    """加载历史记录"""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []


def _strength_style(strength: str) -> str:
    """根据强度返回 rich 颜色样式"""
    styles = {
        "极弱": "bold red", "弱": "red",
        "中等": "yellow", "强": "green",
        "很强": "bold green", "极强": "bold bright_magenta",
    }
    return styles.get(strength, "white")


def show_history():
    """显示历史记录"""
    history = load_history()
    
    if not history:
        console.print("\n[dim]暂无历史记录[/dim]")
        return
    
    table = Table(
        title="密码生成历史",
        box=box.ROUNDED,
        border_style="bright_blue",
        title_style="bold bright_cyan",
        row_styles=["", "dim"],
    )
    table.add_column("序号", style="cyan", justify="center", width=6)
    table.add_column("长度", justify="center", width=6)
    table.add_column("强度", justify="center", width=8)
    table.add_column("熵值 (bits)", justify="center", width=12)
    table.add_column("生成时间", style="dim")
    
    for i, record in enumerate(reversed(history[-20:]), 1):
        created = record.get('created_at', '')[:19].replace('T', ' ')
        strength = record.get('strength', '-')
        style = _strength_style(strength)
        table.add_row(
            str(i),
            str(record.get('length', '-')),
            f"[{style}]{strength}[/{style}]",
            str(record.get('entropy', '-')),
            created,
        )
    
    console.print()
    console.print(table)
    console.print(f"  [dim]共 {len(history)} 条记录（显示最近 20 条） · 历史记录只保存哈希值，不保存明文密码[/dim]\n")


# ==================== 加密存储 ====================

def derive_key(master_password: str, salt: bytes) -> bytes:
    """使用 PBKDF2HMAC 从主密码派生 Fernet 密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))
    return key


def get_or_create_salt() -> bytes:
    """读取或创建盐文件"""
    if SALT_FILE.exists():
        with open(SALT_FILE, 'rb') as f:
            return f.read()
    else:
        salt = os.urandom(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
        return salt


def encrypt_and_save(passwords_data: list, master_password: str):
    """加密密码数据并保存到文件"""
    salt = get_or_create_salt()
    key = derive_key(master_password, salt)
    fernet = Fernet(key)

    # 如果已有加密文件，先解密合并
    existing_data = []
    if ENCRYPTED_FILE.exists():
        try:
            with open(ENCRYPTED_FILE, 'rb') as f:
                encrypted = f.read()
            decrypted = fernet.decrypt(encrypted)
            existing_data = json.loads(decrypted.decode('utf-8'))
        except InvalidToken:
            console.print("\n[bold red]⚠ 警告: 主密码与之前保存时不一致！[/bold red]")
            console.print("  [dim]继续将覆盖已有的旧密码记录，且无法恢复。[/dim]")
            try:
                if not Confirm.ask("是否覆盖旧数据", default=False):
                    console.print("[dim]已取消保存。[/dim]")
                    return
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]已取消[/dim]")
                return
            existing_data = []
        except Exception:
            existing_data = []

    # 合并数据
    existing_data.extend(passwords_data)

    # 加密并保存
    plaintext = json.dumps(existing_data, ensure_ascii=False, indent=2).encode('utf-8')
    encrypted = fernet.encrypt(plaintext)

    with open(ENCRYPTED_FILE, 'wb') as f:
        f.write(encrypted)

    console.print(f"\n[bold green]✓ 已加密保存 {len(passwords_data)} 条密码到:[/bold green] {ENCRYPTED_FILE}")
    console.print(f"  [dim]当前共存储 {len(existing_data)} 条密码记录[/dim]")

    # 触发云端同步（如已配置）
    sync_after_save()


def decrypt_and_load(master_password: str) -> list:
    """解密并加载密码数据"""
    if not ENCRYPTED_FILE.exists():
        console.print("\n[bold yellow]⚠ 暂无加密密码文件，请先生成并保存密码。[/bold yellow]")
        return []

    salt = get_or_create_salt()
    key = derive_key(master_password, salt)
    fernet = Fernet(key)

    with open(ENCRYPTED_FILE, 'rb') as f:
        encrypted = f.read()

    decrypted = fernet.decrypt(encrypted)
    return json.loads(decrypted.decode('utf-8'))


def save_passwords_encrypted(passwords: list, analyses: list):
    """交互式加密保存入口"""
    console.print()
    console.print(Panel(
        "[dim]密码将使用主密码加密后保存，请牢记您的主密码！\n如果忘记主密码，已保存的密码将无法恢复。[/dim]",
        title="[bold bright_cyan]🔐 加密保存密码到本地[/bold bright_cyan]",
        border_style="bright_blue", box=box.ROUNDED, padding=(1, 2),
    ))

    console.print("  [bold]🔒 请输入主密码[/bold] [dim](输入时不会显示字符)[/dim]")
    master_pwd = getpass.getpass("  Master Password: ")
    if not master_pwd:
        console.print("\n[bold red]✗ 主密码不能为空[/bold red]")
        return

    console.print("  [bold]🔒 请再次确认主密码[/bold]")
    confirm_pwd = getpass.getpass("  Confirm Password: ")
    if master_pwd != confirm_pwd:
        console.print("\n[bold red]✗ 两次输入的主密码不一致[/bold red]")
        return

    # 构建保存数据
    passwords_data = []
    for pwd, analysis in zip(passwords, analyses):
        passwords_data.append({
            "password": pwd,
            "length": analysis['length'],
            "entropy": analysis['entropy'],
            "strength": analysis['strength'],
            "created_at": datetime.now().isoformat(),
        })

    try:
        encrypt_and_save(passwords_data, master_pwd)
    except Exception as e:
        console.print(f"\n[bold red]✗ 加密保存失败: {e}[/bold red]")


def read_passwords_encrypted(search: str = ''):
    """交互式解密读取入口"""
    console.print()
    console.print(Panel(
        "[dim]输入主密码以解密查看已保存的密码记录[/dim]",
        title="[bold bright_cyan]🔓 解密读取已保存的密码[/bold bright_cyan]",
        border_style="bright_blue", box=box.ROUNDED, padding=(1, 2),
    ))

    if not ENCRYPTED_FILE.exists():
        console.print("\n[bold yellow]⚠ 暂无加密密码文件，请先生成并保存密码。[/bold yellow]")
        return

    console.print("  [bold]🔒 请输入主密码[/bold] [dim](输入时不会显示字符)[/dim]")
    master_pwd = getpass.getpass("  Master Password: ")

    try:
        data = decrypt_and_load(master_pwd)
    except InvalidToken:
        console.print("\n[bold red]✗ 主密码错误！无法解密。请确认您输入的主密码是否正确。[/bold red]")
        return
    except Exception as e:
        console.print(f"\n[bold red]✗ 解密失败: {e}[/bold red]")
        return

    if not data:
        console.print("\n[dim]暂无已保存的密码记录。[/dim]")
        return

    # 搜索/过滤
    if search:
        data = [r for r in data if search.lower() in r.get('password', '').lower()
                or search.lower() in r.get('strength', '').lower()]
        if not data:
            console.print(f"\n[bold yellow]⚠ 未找到包含 \"{search}\" 的记录。[/bold yellow]")
            return
        console.print(f"\n[bold green]✓ 解密成功！[/bold green]搜索 \"{search}\" 匹配 [bold]{len(data)}[/bold] 条记录：")
    else:
        console.print(f"\n[bold green]✓ 解密成功！[/bold green]共找到 [bold]{len(data)}[/bold] 条密码记录：")

    table = Table(
        box=box.ROUNDED,
        border_style="green",
        row_styles=["", "dim"],
    )
    table.add_column("序号", style="cyan", justify="center", width=6)
    table.add_column("密码", style="bold bright_white", min_width=20)
    table.add_column("长度", justify="center", width=6)
    table.add_column("强度", justify="center", width=8)
    table.add_column("熵值", justify="center", width=10)
    table.add_column("保存时间", style="dim")

    # 默认隐藏密码，显示掩码
    hidden_map = {}
    for i, record in enumerate(data, 1):
        pwd = record.get('password', '???')
        hidden_map[i] = pwd
        masked = pwd[:2] + '•' * max(len(pwd) - 4, 4) + pwd[-2:] if len(pwd) > 4 else '•' * len(pwd)
        strength = record.get('strength', '-')
        style = _strength_style(strength)
        table.add_row(
            str(i),
            masked,
            str(record.get('length', '-')),
            f"[{style}]{strength}[/{style}]",
            str(record.get('entropy', '-')),
            record.get('created_at', '')[:19].replace('T', ' '),
        )

    console.print(table)
    console.print(f"  [dim]共 {len(data)} 条记录 · 密码已隐藏[/dim]")
    console.print("  [dim]输入序号可查看明文密码 (直接回车返回)[/dim]")

    # 按需查看明文
    try:
        reveal = Prompt.ask("\n  [bold cyan]查看明文[/bold]", default='').strip()
        if reveal.isdigit() and 1 <= int(reveal) <= len(data):
            idx = int(reveal)
            real_pwd = hidden_map[idx]
            console.print(Panel(
                f"[bold bright_white]{real_pwd}[/bold bright_white]",
                title=f"[bold green]第 {idx} 条密码[/bold green]",
                border_style="green", box=box.ROUNDED, padding=(1, 2),
            ))
            if copy_to_clipboard(real_pwd):
                console.print("[bold green]✓ 已复制到剪贴板[/bold green]")
            console.print("[bold yellow]⚠ 密码已在终端明文显示，阅读后请及时清屏。[/bold yellow]")
    except (EOFError, KeyboardInterrupt):
        pass

    console.print()


# ==================== SFTP 云端同步 ====================

def sftp_is_configured() -> bool:
    """检查 SFTP 配置是否完整"""
    if not HAS_PARAMIKO:
        return False
    return bool(SFTP_HOST and SFTP_USER)


def create_sftp_client() -> tuple:
    """建立 SSH 连接并返回 (ssh_client, sftp_client)"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    connect_kwargs = {
        "hostname": SFTP_HOST,
        "port": SFTP_PORT,
        "username": SFTP_USER,
        "timeout": 10,
    }

    # 密钥认证优先
    if SFTP_KEY_PATH:
        key_path = os.path.expanduser(SFTP_KEY_PATH)
        if os.path.exists(key_path):
            connect_kwargs["key_filename"] = key_path
        elif SFTP_PASSWORD:
            connect_kwargs["password"] = SFTP_PASSWORD
    elif SFTP_PASSWORD:
        connect_kwargs["password"] = SFTP_PASSWORD

    ssh.connect(**connect_kwargs)
    sftp = ssh.open_sftp()
    return ssh, sftp


def _ensure_remote_dir(sftp):
    """确保远程目录存在"""
    try:
        sftp.stat(REMOTE_DIR)
    except FileNotFoundError:
        # 逐级创建目录
        parts = REMOTE_DIR.replace("\\", "/").split("/")
        current = ""
        for part in parts:
            if not part:
                current = "/"
                continue
            current = current + part + "/" if current.endswith("/") else current + "/" + part
            try:
                sftp.stat(current)
            except FileNotFoundError:
                sftp.mkdir(current)


def _get_remote_mtime(sftp, remote_path: str) -> float:
    """获取远程文件的修改时间，文件不存在返回 0"""
    try:
        return float(sftp.stat(remote_path).st_mtime)
    except FileNotFoundError:
        return 0.0


def _get_local_mtime(local_path) -> float:
    """获取本地文件的修改时间，文件不存在返回 0"""
    try:
        return os.path.getmtime(local_path)
    except (OSError, FileNotFoundError):
        return 0.0


def sftp_push(force: bool = False):
    """上传 .enc + .salt 到远程服务器（含时间戳比对）"""
    if not sftp_is_configured():
        console.print("\n[bold yellow]⚠ SFTP 未配置，跳过云端同步。请配置 .env 文件后重试。[/bold yellow]")
        return

    if not ENCRYPTED_FILE.exists():
        console.print("\n[bold yellow]⚠ 本地无加密文件，请先生成并保存密码。[/bold yellow]")
        return

    console.print("\n[bold blue]☁ 正在连接 SFTP 服务器...[/bold blue]")

    try:
        ssh, sftp = create_sftp_client()
    except paramiko.AuthenticationException:
        console.print("[bold red]✗ SFTP 认证失败，请检查用户名/密码/密钥配置。[/bold red]")
        return
    except (paramiko.SSHException, socket.timeout, OSError) as e:
        console.print(f"[bold red]✗ SFTP 连接失败: {e}[/bold red]")
        return

    try:
        _ensure_remote_dir(sftp)

        remote_enc = REMOTE_DIR.rstrip("/") + "/" + ENCRYPTED_FILE.name
        remote_salt = REMOTE_DIR.rstrip("/") + "/" + SALT_FILE.name

        # 时间戳比对
        if not force:
            local_mtime = _get_local_mtime(ENCRYPTED_FILE)
            remote_mtime = _get_remote_mtime(sftp, remote_enc)

            if remote_mtime > 0 and local_mtime < remote_mtime:
                console.print("\n[bold red]⚠️ 发现服务器端有更新的密码记录！强制上传将覆盖远端数据。[/bold red]")
                try:
                    if not Confirm.ask("是否继续", default=False):
                        console.print("[dim]已取消上传。建议先执行 --sync-pull 拉取最新数据。[/dim]")
                        return
                except (EOFError, KeyboardInterrupt):
                    console.print("\n[dim]已取消[/dim]")
                    return

        # 上传文件
        sftp.put(str(ENCRYPTED_FILE), remote_enc)
        if SALT_FILE.exists():
            sftp.put(str(SALT_FILE), remote_salt)

        console.print(f"[bold green]✓ 已上传到 {SFTP_HOST}:{REMOTE_DIR}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]✗ 上传失败: {e}[/bold red]")
    finally:
        sftp.close()
        ssh.close()


def sftp_pull(force: bool = False):
    """从远程服务器下载 .enc + .salt 到本地（含时间戳比对）"""
    if not sftp_is_configured():
        console.print("\n[bold yellow]⚠ SFTP 未配置，请配置 .env 文件后重试。[/bold yellow]")
        return

    console.print("\n[bold blue]☁ 正在连接 SFTP 服务器...[/bold blue]")

    try:
        ssh, sftp = create_sftp_client()
    except paramiko.AuthenticationException:
        console.print("[bold red]✗ SFTP 认证失败，请检查用户名/密码/密钥配置。[/bold red]")
        return
    except (paramiko.SSHException, socket.timeout, OSError) as e:
        console.print(f"[bold red]✗ SFTP 连接失败: {e}[/bold red]")
        return

    try:
        remote_enc = REMOTE_DIR.rstrip("/") + "/" + ENCRYPTED_FILE.name
        remote_salt = REMOTE_DIR.rstrip("/") + "/" + SALT_FILE.name

        # 检查远程文件是否存在
        remote_mtime = _get_remote_mtime(sftp, remote_enc)
        if remote_mtime == 0:
            console.print("\n[bold yellow]⚠ 服务器上暂无密码文件。[/bold yellow]")
            return

        # 时间戳比对
        if not force:
            local_mtime = _get_local_mtime(ENCRYPTED_FILE)

            if local_mtime > 0 and remote_mtime < local_mtime:
                console.print("\n[bold red]⚠️ 本地密码记录比服务器端更新！强制拉取将丢失本地最新修改。[/bold red]")
                try:
                    if not Confirm.ask("是否继续", default=False):
                        console.print("[dim]已取消拉取。建议先执行 --sync-push 上传本地数据。[/dim]")
                        return
                except (EOFError, KeyboardInterrupt):
                    console.print("\n[dim]已取消[/dim]")
                    return

        # 下载文件
        sftp.get(remote_enc, str(ENCRYPTED_FILE))
        try:
            sftp.get(remote_salt, str(SALT_FILE))
        except FileNotFoundError:
            console.print("  [yellow]⚠ 远程盐文件不存在，仅拉取了加密文件。[/yellow]")

        console.print(f"[bold green]✓ 已从 {SFTP_HOST}:{REMOTE_DIR} 拉取到本地[/bold green]")

    except FileNotFoundError:
        console.print("\n[bold yellow]⚠ 服务器上未找到密码文件。[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]✗ 拉取失败: {e}[/bold red]")
    finally:
        sftp.close()
        ssh.close()


def sync_after_save():
    """保存后自动同步钩子（仅在 SFTP 已配置时触发，失败时重试 1 次）"""
    if not sftp_is_configured():
        return

    import time
    max_retries = 1
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                console.print(f"[bold blue]☁ 第 {attempt + 1} 次尝试同步...[/bold blue]")
            else:
                console.print("\n[bold blue]☁ 正在同步到云端...[/bold blue]")
            ssh, sftp = create_sftp_client()

            try:
                _ensure_remote_dir(sftp)

                remote_enc = REMOTE_DIR.rstrip("/") + "/" + ENCRYPTED_FILE.name
                remote_salt = REMOTE_DIR.rstrip("/") + "/" + SALT_FILE.name

                # 自动同步时：本地刚保存，一定是最新的，直接上传
                sftp.put(str(ENCRYPTED_FILE), remote_enc)
                if SALT_FILE.exists():
                    sftp.put(str(SALT_FILE), remote_salt)

                console.print(f"[bold green]✓ 云端同步完成 ({SFTP_HOST})[/bold green]")
            finally:
                sftp.close()
                ssh.close()

            return  # 成功，直接返回

        except Exception as e:
            if attempt < max_retries:
                console.print(f"[bold yellow]⚠ 同步失败，3 秒后重试: {e}[/bold yellow]")
                time.sleep(3)
            else:
                console.print(f"[bold yellow]⚠ 云端同步失败，已保存至本地: {e}[/bold yellow]")


# ==================== 输出格式 ====================

def output_json(passwords: list, analyses: list) -> str:
    """JSON 格式输出"""
    data = {
        "generated_at": datetime.now().isoformat(),
        "count": len(passwords),
        "passwords": [
            {
                "index": i + 1,
                "password": pwd,
                "analysis": analyses[i]
            }
            for i, pwd in enumerate(passwords)
        ]
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def save_to_file(content: str, filepath: str, format_type: str = "text"):
    """保存到文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        console.print(f"\n[bold green]✓ 已保存到文件:[/bold green] {filepath}")
    except Exception as e:
        console.print(f"\n[bold red]✗ 保存失败: {e}[/bold red]")


# ==================== 交互界面 ====================

def print_banner():
    """打印横幅"""
    banner_text = Text()
    banner_text.append("强密码生成器", style="bold bright_cyan")
    banner_text.append(" v2.0", style="bold bright_blue")

    features = Text()
    features.append("可配置长度", style="bright_white")
    features.append(" · ", style="dim")
    features.append("强度评估", style="bright_white")
    features.append(" · ", style="dim")
    features.append("排除混淆字符", style="bright_white")
    features.append(" · ", style="dim")
    features.append("加密存储", style="bright_green")
    features.append(" · ", style="dim")
    features.append("云端同步", style="bright_blue")

    panel = Panel(
        features,
        title=banner_text,
        border_style="bright_blue",
        box=box.DOUBLE_EDGE,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)


def print_password_card(index: int, analysis: dict, show_analysis: bool = True):
    """打印密码卡片"""
    pwd = analysis['password']
    
    console.print(f"  [bold cyan]\\[{index}][/bold cyan] [bold bright_white]{pwd}[/bold bright_white]")
    
    if show_analysis:
        strength = analysis['strength']
        entropy = analysis['entropy']
        crack_time = analysis['crack_time']
        style = _strength_style(strength)
        console.print(f"      [{style}]● {strength}[/{style}] [dim]|[/dim] 熵值: [bold]{entropy}[/bold] bits [dim]|[/dim] 破解时间: [bold]{crack_time}[/bold]")
        console.print()


def interactive_mode(args):
    """交互模式"""
    print_banner()
    
    # 显示当前配置
    console.print(f"[dim]当前配置: 长度={args.length}, 数量={args.count}, "
                  f"排除混淆字符={'是' if args.exclude_confusing else '否'}[/dim]")
    console.print()
    
    passwords = []
    analyses = []
    
    def generate_passwords():
        nonlocal passwords, analyses
        passwords = []
        analyses = []
        
        console.rule("[bold bright_cyan]生成的密码[/bold bright_cyan]", style="bright_blue")
        console.print()
        
        for i in range(args.count):
            pwd = generate_strong_password(
                args.length,
                exclude_confusing=args.exclude_confusing,
                include_uppercase=not args.no_uppercase,
                include_lowercase=not args.no_lowercase,
                include_digits=not args.no_digits,
                include_special=not args.no_special
            )
            passwords.append(pwd)
            analysis = analyze_password(pwd)
            analyses.append(analysis)
            print_password_card(i + 1, analysis)
        
        console.rule(style="bright_blue")
    
    generate_passwords()
    
    while True:
        console.print()
        cmd_parts = [f"[bold cyan]\\[1-{args.count}][/bold cyan] 选择密码"]
        cmd_parts.append("[bold cyan]\\[r][/bold cyan] 重新生成")
        cmd_parts.append("[bold cyan]\\[l][/bold cyan] 修改长度")
        cmd_parts.append("[bold cyan]\\[s][/bold cyan] 加密保存")
        cmd_parts.append("[bold cyan]\\[d][/bold cyan] 解密查看")
        if sftp_is_configured():
            cmd_parts.append("[bold cyan]\\[u][/bold cyan] 上传同步")
            cmd_parts.append("[bold cyan]\\[p][/bold cyan] 拉取同步")
        cmd_parts.append("[bold cyan]\\[h][/bold cyan] 历史记录")
        cmd_parts.append("[bold cyan]\\[q][/bold cyan] 退出")
        console.print(" | ".join(cmd_parts))
        
        try:
            choice = Prompt.ask("[bold]请输入[/bold]").strip().lower()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]退出[/dim]")
            sys.exit(0)
        
        # 选择密码
        if choice.isdigit() and 1 <= int(choice) <= args.count:
            idx = int(choice) - 1
            selected = passwords[idx]
            analysis = analyses[idx]
            
            console.print()
            console.print(Panel(
                f"[bold bright_white]{selected}[/bold bright_white]",
                title="[bold green]你选择的密码[/bold green]",
                border_style="green", box=box.ROUNDED, padding=(1, 2),
            ))
            
            if copy_to_clipboard(selected):
                console.print("[bold green]✓ 密码已复制到剪贴板[/bold green]")
            
            # 保存到历史
            if not args.no_history:
                save_to_history(selected, analysis)
                console.print("[bold green]✓ 已记录到历史（仅保存哈希）[/bold green]")
            
            console.print()
            
            # 询问是否继续
            try:
                if not Confirm.ask("继续生成", default=True):
                    break
            except (EOFError, KeyboardInterrupt):
                break
            generate_passwords()
        
        # 重新生成
        elif choice == 'r':
            console.print("\n[dim]重新生成...[/dim]\n")
            generate_passwords()
        
        # 修改长度
        elif choice == 'l':
            try:
                new_length = IntPrompt.ask(f"请输入新的密码长度 ({MIN_LENGTH}-{MAX_LENGTH})")
                if MIN_LENGTH <= new_length <= MAX_LENGTH:
                    args.length = new_length
                    console.print(f"\n[bold green]✓ 密码长度已更新为: {new_length}[/bold green]\n")
                    generate_passwords()
                else:
                    console.print(f"[bold red]长度必须在 {MIN_LENGTH}-{MAX_LENGTH} 之间[/bold red]")
            except (ValueError, KeyboardInterrupt):
                console.print("[bold red]请输入有效的数字[/bold red]")
        
        # 加密保存
        elif choice == 's':
            if not passwords:
                console.print("\n[bold yellow]⚠ 暂无可保存的密码，请先生成密码。[/bold yellow]")
                continue
            save_passwords_encrypted(passwords, analyses)
        
        # 解密查看
        elif choice == 'd':
            read_passwords_encrypted()
        
        # 上传同步
        elif choice == 'u':
            sftp_push()
        
        # 拉取同步
        elif choice == 'p':
            sftp_pull()
        
        # 历史记录
        elif choice == 'h':
            show_history()
        
        # 退出
        elif choice == 'q':
            console.print("[dim]退出[/dim]")
            break
        
        else:
            console.print("[bold red]无效输入[/bold red]")


def batch_mode(args):
    """批量模式（非交互）"""
    passwords = []
    analyses = []
    
    for _ in range(args.count):
        pwd = generate_strong_password(
            args.length,
            exclude_confusing=args.exclude_confusing,
            include_uppercase=not args.no_uppercase,
            include_lowercase=not args.no_lowercase,
            include_digits=not args.no_digits,
            include_special=not args.no_special
        )
        passwords.append(pwd)
        analyses.append(analyze_password(pwd))
    
    # JSON 输出
    if args.json:
        output = output_json(passwords, analyses)
        if args.output:
            save_to_file(output, args.output, "json")
        else:
            print(output)
        return
    
    # 纯文本输出（每行一个密码）
    if args.plain:
        output = '\n'.join(passwords)
        if args.output:
            save_to_file(output, args.output, "text")
        else:
            print(output)
        return
    
    # 默认格式输出
    print_banner()
    console.rule("[bold bright_cyan]生成的密码[/bold bright_cyan]", style="bright_blue")
    console.print()
    
    for i, (pwd, analysis) in enumerate(zip(passwords, analyses)):
        print_password_card(i + 1, analysis, show_analysis=not args.no_analysis)
    
    console.rule(style="bright_blue")
    
    if args.save_encrypted:
        save_passwords_encrypted(passwords, analyses)
    elif args.output:
        content = '\n'.join(passwords)
        save_to_file(content, args.output, "text")


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(
        description="强密码生成器 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                          # 交互模式，默认12位
  %(prog)s -l 16                    # 生成16位密码
  %(prog)s -l 20 -c 5               # 生成5个20位密码
  %(prog)s -l 16 -e                 # 排除易混淆字符
  %(prog)s -l 16 --json             # JSON格式输出
  %(prog)s -l 16 -o passwords.txt   # 保存到文件
  %(prog)s --history                # 查看历史记录
        """
    )
    
    # 基本选项
    parser.add_argument('-l', '--length', type=int, default=DEFAULT_LENGTH,
                        help=f'密码长度 (默认: {DEFAULT_LENGTH}, 范围: {MIN_LENGTH}-{MAX_LENGTH})')
    parser.add_argument('-c', '--count', type=int, default=DEFAULT_COUNT,
                        help=f'生成数量 (默认: {DEFAULT_COUNT})')
    
    # 字符集选项
    parser.add_argument('-e', '--exclude-confusing', action='store_true',
                        help='排除易混淆字符 (0O1lI|)')
    parser.add_argument('--no-uppercase', action='store_true',
                        help='不包含大写字母')
    parser.add_argument('--no-lowercase', action='store_true',
                        help='不包含小写字母')
    parser.add_argument('--no-digits', action='store_true',
                        help='不包含数字')
    parser.add_argument('--no-special', action='store_true',
                        help='不包含特殊字符')
    
    # 输出选项
    parser.add_argument('--json', action='store_true',
                        help='JSON格式输出')
    parser.add_argument('--plain', action='store_true',
                        help='纯文本输出（每行一个密码）')
    parser.add_argument('-o', '--output', type=str,
                        help='输出到文件')
    parser.add_argument('--no-analysis', action='store_true',
                        help='不显示密码分析')
    
    # 历史记录
    parser.add_argument('--history', action='store_true',
                        help='显示历史记录')
    parser.add_argument('--no-history', action='store_true',
                        help='不保存到历史记录')
    
    # 加密存储
    parser.add_argument('--save-encrypted', action='store_true',
                        help='将生成的密码加密保存到本地')
    parser.add_argument('--read-encrypted', action='store_true',
                        help='解密读取已保存的密码')
    parser.add_argument('--search', type=str, default='',
                        help='解密读取时按关键词过滤密码或强度')
    
    # SFTP 云端同步
    parser.add_argument('--sync-push', action='store_true',
                        help='手动上传加密文件到 SFTP 服务器')
    parser.add_argument('--sync-pull', action='store_true',
                        help='从 SFTP 服务器拉取加密文件到本地')
    parser.add_argument('--force', action='store_true',
                        help='强制同步，跳过时间戳比对检查')
    
    # 非交互模式
    parser.add_argument('-b', '--batch', action='store_true',
                        help='批量模式（非交互）')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.length < MIN_LENGTH or args.length > MAX_LENGTH:
        console.print(f"[bold red]错误: 密码长度必须在 {MIN_LENGTH}-{MAX_LENGTH} 之间[/bold red]")
        sys.exit(1)
    
    if args.count < 1 or args.count > 100:
        console.print("[bold red]错误: 生成数量必须在 1-100 之间[/bold red]")
        sys.exit(1)
    
    # 显示历史记录
    if args.history:
        show_history()
        return
    
    # 解密读取模式
    if args.read_encrypted:
        read_passwords_encrypted(search=args.search)
        return
    
    # SFTP 同步模式
    if args.sync_push:
        sftp_push(force=args.force)
        return
    
    if args.sync_pull:
        sftp_pull(force=args.force)
        return
    
    # 批量模式或有输出选项时使用非交互模式
    if args.batch or args.json or args.plain or args.output:
        batch_mode(args)
    else:
        interactive_mode(args)


if __name__ == "__main__":
    main()

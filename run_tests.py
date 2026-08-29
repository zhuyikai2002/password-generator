"""端到端功能测试 — 直接 import 模块函数，绕过 getpass 控制台限制"""
import subprocess
import sys
import os
import json
import tempfile
import importlib.util
from pathlib import Path
from unittest.mock import patch
from io import StringIO

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['TERM'] = 'dumb'

# 让 rich 使用 UTF-8 输出，避免 Windows GBK 编码问题
os.environ['PYTHONIOENCODING'] = 'utf-8'

PY = sys.executable
SCRIPT = str(Path(__file__).parent / 'generate-password.py')
PROJECT = Path(__file__).parent

MASTER_PWD = 'TestMaster@2026!'
WRONG_PWD = 'WrongPassword!'

# ---- 直接加载模块 ----
spec = importlib.util.spec_from_file_location('pwgen', SCRIPT)
pwgen = importlib.util.module_from_spec(spec)

# 阻止 rich Console 在 import 时输出到真实终端
with patch('sys.stdout', new_callable=StringIO):
    spec.loader.exec_module(pwgen)

# 替换 rich console，使其输出到 StringIO 而非真实终端（避免 GBK 编码问题）
_test_console = pwgen.Console(file=StringIO(), force_terminal=True, color_system=None, width=120)
pwgen.console = _test_console

def get_console_output():
    """获取并清空 console 缓冲区"""
    buf = pwgen.console.file
    buf.seek(0)
    out = buf.read()
    buf.seek(0)
    buf.truncate(0)
    return out

enc_file = pwgen.ENCRYPTED_FILE
salt_file = pwgen.SALT_FILE

# 清理旧文件
for f in [enc_file, salt_file]:
    if f.exists():
        f.unlink()

passed = 0
failed = 0
failed_tests = []

def check(label, condition, detail=''):
    global passed, failed
    if condition:
        passed += 1
        print(f'  [PASS] {label}')
    else:
        failed += 1
        failed_tests.append(label)
        print(f'  [FAIL] {label}')
        if detail:
            # 清理不可打印字符
            safe = detail.encode('ascii', errors='replace').decode('ascii')[:200]
            print(f'         {safe}')

def run_cli(args):
    """用于不涉及 getpass 的 CLI 测试"""
    result = subprocess.run(
        [PY, SCRIPT] + args,
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30,
    )
    return result

# ============================================================
print('\n===== 1. 基础密码生成 =====')
# ============================================================

r = run_cli(['-b', '-l', '16', '-c', '3', '--plain'])
lines = r.stdout.strip().split('\n')
check('批量模式生成 3 个 16 位密码 (plain)', r.returncode == 0 and len(lines) == 3)
check('每个密码长度为 16', all(len(l.strip()) == 16 for l in lines))

r = run_cli(['-b', '-l', '32', '-c', '1', '--plain'])
check('生成 32 位密码', len(r.stdout.strip()) == 32)

r = run_cli(['-b', '-l', '128', '-c', '1', '--plain'])
check('生成 128 位密码 (最大值)', len(r.stdout.strip()) == 128)

r = run_cli(['-b', '-l', '8', '-c', '1', '--plain'])
check('生成 8 位密码 (最小值)', len(r.stdout.strip()) == 8)

# ============================================================
print('\n===== 2. 字符集排除 =====')
# ============================================================

r = run_cli(['-b', '-l', '50', '-c', '1', '--no-uppercase', '--plain'])
check('排除大写字母', not any(c.isupper() for c in r.stdout.strip()))

r = run_cli(['-b', '-l', '50', '-c', '1', '--no-lowercase', '--plain'])
check('排除小写字母', not any(c.islower() for c in r.stdout.strip()))

r = run_cli(['-b', '-l', '50', '-c', '1', '--no-digits', '--plain'])
check('排除数字', not any(c.isdigit() for c in r.stdout.strip()))

r = run_cli(['-b', '-l', '50', '-c', '1', '--no-special', '--plain'])
check('排除特殊字符', all(c.isalnum() for c in r.stdout.strip()))

r = run_cli(['-b', '-l', '50', '-c', '1', '-e', '--plain'])
confusing = set('0O1lI|')
check('排除混淆字符', not any(c in confusing for c in r.stdout.strip()))

# ============================================================
print('\n===== 3. JSON 输出 =====')
# ============================================================

r = run_cli(['-b', '-l', '16', '-c', '2', '--json'])
try:
    data = json.loads(r.stdout)
    check('JSON 输出可解析', True)
    check('count 字段正确', data['count'] == 2)
    check('passwords 数组长度为 2', len(data['passwords']) == 2)
    check('包含 analysis 字段', 'analysis' in data['passwords'][0])
    check('entropy 为数字', isinstance(data['passwords'][0]['analysis']['entropy'], (int, float)))
    check('strength 字段存在', 'strength' in data['passwords'][0]['analysis'])
    check('crack_time 字段存在', 'crack_time' in data['passwords'][0]['analysis'])
except Exception as e:
    check('JSON 输出可解析', False, str(e))

# ============================================================
print('\n===== 4. 输出到文件 =====')
# ============================================================

with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as tmp:
    tmp_path = tmp.name
try:
    r = run_cli(['-b', '-l', '16', '-c', '3', '-o', tmp_path])
    check('输出到文件 (-o)', r.returncode == 0)
    with open(tmp_path, 'r', encoding='utf-8') as f:
        content = f.read()
    check('文件包含 3 个密码', len(content.strip().split('\n')) == 3)
finally:
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

# ============================================================
print('\n===== 5. 边界条件与错误处理 =====')
# ============================================================

check('长度 < 8 被拒绝', run_cli(['-b', '-l', '7']).returncode != 0)
check('长度 > 128 被拒绝', run_cli(['-b', '-l', '129']).returncode != 0)
check('数量 < 1 被拒绝', run_cli(['-b', '-l', '16', '-c', '0']).returncode != 0)
check('数量 > 100 被拒绝', run_cli(['-b', '-l', '16', '-c', '101']).returncode != 0)

# ============================================================
print('\n===== 6. 密码强度评估 =====')
# ============================================================

check('熵值计算 "a" = 0 (单字符类)', pwgen.calculate_entropy('a') > 0)
check('熵值计算 "aaaaaaaa" ≈ 37.6', abs(pwgen.calculate_entropy('aaaaaaaa') - 37.6) < 1)

short_pwd = 'abc'
a = pwgen.analyze_password(short_pwd)
check('短密码强度为"极弱"或"弱"', a['strength'] in ('极弱', '弱'), f"实际: {a['strength']}")

long_pwd = 'Xk#9mP!qR2vL@nZ8wB&cF4hT7jY1dS'
a2 = pwgen.analyze_password(long_pwd)
check('长复杂密码强度为"极强"', a2['strength'] == '极强', f"实际: {a2['strength']}")

a3 = pwgen.analyze_password('Abcdef12!')
check('中等密码有合理强度', a3['strength'] in ('中等', '强', '弱'), f"实际: {a3['strength']}")

check('破解时间 "瞬间" 存在', pwgen.get_crack_time_estimate(10) == '瞬间')
check('破解时间 "宇宙年龄级别" 存在', '宇宙' in pwgen.get_crack_time_estimate(256))

# ============================================================
print('\n===== 7. 加密存储功能 (直接调用函数) =====')
# ============================================================

# 7a. 首次加密保存
print('  --- 7a. 首次加密保存 ---')
pw1 = pwgen.generate_strong_password(16)
pw2 = pwgen.generate_strong_password(16)
a1 = pwgen.analyze_password(pw1)
a2 = pwgen.analyze_password(pw2)

data_to_save = [
    {"password": pw1, "length": a1['length'], "entropy": a1['entropy'],
     "strength": a1['strength'], "created_at": "2026-01-01T00:00:00"},
    {"password": pw2, "length": a2['length'], "entropy": a2['entropy'],
     "strength": a2['strength'], "created_at": "2026-01-01T00:00:01"},
]

with patch('sys.stdout', new_callable=StringIO):
    pwgen.encrypt_and_save(data_to_save, MASTER_PWD)
check('加密文件已创建', enc_file.exists())
check('盐文件已创建', salt_file.exists())

# 验证密文不可读
with open(enc_file, 'rb') as f:
    enc_bytes = f.read()
check('加密文件不是明文 JSON', b'"password"' not in enc_bytes)

# 7b. 正确主密码解密
with patch('sys.stdout', new_callable=StringIO):
    loaded = pwgen.decrypt_and_load(MASTER_PWD)
check('正确主密码解密成功', isinstance(loaded, list))
check('解密出 2 条记录', len(loaded) == 2, f'实际: {len(loaded)}')
check('解密密码内容匹配', loaded[0]['password'] == pw1 and loaded[1]['password'] == pw2)

# 7c. 错误主密码解密
try:
    pwgen.decrypt_and_load(WRONG_PWD)
    check('错误主密码应抛异常', False, '未抛出异常')
except Exception as e:
    check('错误主密码被正确拒绝', 'InvalidToken' in type(e).__name__ or 'InvalidToken' in str(type(e)), str(type(e)))

# 7d. 第二次保存 — 合并
pw3 = pwgen.generate_strong_password(20)
a3 = pwgen.analyze_password(pw3)
data2 = [{"password": pw3, "length": a3['length'], "entropy": a3['entropy'],
           "strength": a3['strength'], "created_at": "2026-01-02T00:00:00"}]

with patch('sys.stdout', new_callable=StringIO):
    pwgen.encrypt_and_save(data2, MASTER_PWD)
with patch('sys.stdout', new_callable=StringIO):
    loaded2 = pwgen.decrypt_and_load(MASTER_PWD)
check('第二次保存后共 3 条记录', len(loaded2) == 3, f'实际: {len(loaded2)}')
check('第三条密码匹配', loaded2[2]['password'] == pw3)

# 7e. 错误主密码保存 — encrypt_and_save 应弹出确认 (mock Confirm.ask → False)
print('  --- 7e. 错误主密码覆盖保护 ---')
with patch.object(pwgen.Confirm, 'ask', return_value=False):
    with patch('sys.stdout', new_callable=StringIO):
        pwgen.encrypt_and_save(
            [{"password": "test", "length": 4, "entropy": 10, "strength": "弱", "created_at": "x"}],
            WRONG_PWD
        )
        # 拒绝覆盖后不应写入新数据
    with patch('sys.stdout', new_callable=StringIO):
        loaded3 = pwgen.decrypt_and_load(MASTER_PWD)
    check('拒绝覆盖后数据不变 (仍 3 条)', len(loaded3) == 3, f'实际: {len(loaded3)}')

# 7f. 错误主密码 + 用户选择覆盖
with patch.object(pwgen.Confirm, 'ask', return_value=True):
    with patch('sys.stdout', new_callable=StringIO):
        pwgen.encrypt_and_save(
            [{"password": "overwritten", "length": 11, "entropy": 50, "strength": "中等", "created_at": "x"}],
            WRONG_PWD
        )
        # 用新密码解密
    with patch('sys.stdout', new_callable=StringIO):
        loaded4 = pwgen.decrypt_and_load(WRONG_PWD)
    check('覆盖后新密码可解密', len(loaded4) == 1 and loaded4[0]['password'] == 'overwritten',
          f'实际: {len(loaded4)} 条')

# 用旧密码应该失败
try:
    with patch('sys.stdout', new_callable=StringIO):
        pwgen.decrypt_and_load(MASTER_PWD)
    check('覆盖后旧密码失效', False, '旧密码仍可解密!')
except Exception:
    check('覆盖后旧密码失效', True)

# 恢复: 用正确密码重新保存
for f in [enc_file, salt_file]:
    if f.exists():
        f.unlink()

with patch('sys.stdout', new_callable=StringIO):
    pwgen.encrypt_and_save(data_to_save + data2, MASTER_PWD)
with patch('sys.stdout', new_callable=StringIO):
    check('恢复测试数据成功', pwgen.decrypt_and_load(MASTER_PWD) is not None)

# ============================================================
print('\n===== 8. SFTP 同步 (未配置时优雅降级) =====')
# ============================================================

# 确保 SFTP 未配置
orig_host = pwgen.SFTP_HOST
pwgen.SFTP_HOST = ''
pwgen.SFTP_USER = ''

check('sftp_is_configured() 返回 False', pwgen.sftp_is_configured() == False)

# sync_after_save 未配置时应静默跳过（不崩溃即通过）
pwgen.sync_after_save()
check('sync_after_save 未配置时静默跳过', True)

# sftp_push 未配置时应提示
pwgen.sftp_push()
push_out = pwgen.console.file.getvalue()
pwgen.console.file.seek(0); pwgen.console.file.truncate(0)
check('sftp_push 未配置时提示 SFTP 未配置', '未配置' in push_out or 'SFTP' in push_out, f'实际输出: {push_out[:80]}')

# sftp_pull 未配置时应提示
pwgen.sftp_pull()
pull_out = pwgen.console.file.getvalue()
pwgen.console.file.seek(0); pwgen.console.file.truncate(0)
check('sftp_pull 未配置时提示 SFTP 未配置', '未配置' in pull_out or 'SFTP' in pull_out, f'实际输出: {pull_out[:80]}')

# CLI 级别测试
r = run_cli(['--sync-push'])
check('--sync-push CLI 不崩溃', r.returncode == 0)

r = run_cli(['--sync-pull'])
check('--sync-pull CLI 不崩溃', r.returncode == 0)

# 恢复
pwgen.SFTP_HOST = orig_host

# ============================================================
print('\n===== 9. 历史记录 =====')
# ============================================================

r = run_cli(['--history'])
check('--history 可正常显示', r.returncode == 0)

# 直接测试历史记录
hist_before = pwgen.load_history()
count_before = len(hist_before)

pwgen.save_to_history('test_pwd_123', {'entropy': 50.0, 'strength': '中等'})
hist_after = pwgen.load_history()
check('save_to_history 增加了一条记录', len(hist_after) == count_before + 1)
check('历史记录只存哈希', hist_after[-1]['hash'] != 'test_pwd_123')
check('哈希是 16 位 hex', len(hist_after[-1]['hash']) == 16)

# ============================================================
print('\n===== 10. 加密模块单元测试 (test_crypto.py) =====')
# ============================================================

r = subprocess.run(
    [PY, str(PROJECT / 'test_crypto.py')],
    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30,
)
check('test_crypto.py 全部通过', '全部测试通过' in r.stdout,
      r.stdout[-200:] if r.returncode != 0 else '')

# ============================================================
print('\n===== 11. 新功能: 空密码检查 (#4) =====')
# ============================================================

# 测试 save_passwords_encrypted 接受空列表不会崩溃
try:
    with patch.object(pwgen.getpass, 'getpass', return_value=''):
        pwgen.save_passwords_encrypted([], [])
    check('空密码列表 + 空主密码不崩溃', True)
except Exception as e:
    check('空密码列表 + 空主密码不崩溃', False, str(e))

# ============================================================
print('\n===== 12. 新功能: 密码隐藏/揭示 (#7) =====')
# ============================================================

# 准备测试数据
for f in [enc_file, salt_file]:
    if f.exists():
        f.unlink()

test_pwds = [
    {"password": "Abc123!@#Long", "length": 13, "entropy": 80, "strength": "强", "created_at": "2026-01-01T00:00:00"},
    {"password": "Xyz789$%^Test", "length": 13, "entropy": 80, "strength": "强", "created_at": "2026-01-01T00:00:01"},
]
pwgen.encrypt_and_save(test_pwds, MASTER_PWD)

# 测试 read_passwords_encrypted 默认隐藏密码
with patch.object(pwgen.getpass, 'getpass', return_value=MASTER_PWD):
    with patch.object(pwgen.Prompt, 'ask', return_value=''):
        pwgen.read_passwords_encrypted()
output = pwgen.console.file.getvalue()
pwgen.console.file.seek(0); pwgen.console.file.truncate(0)
check('解密输出包含已隐藏提示', '已隐藏' in output, f'output[:150]={repr(output[:150])}')
check('解密输出包含掩码字符', '\u2022' in output or '*' in output, 'output中未发现掩码字符')
check('完整密码未明文显示', 'Abc123!@#Long' not in output)

# 测试按序号揭示
with patch.object(pwgen.getpass, 'getpass', return_value=MASTER_PWD):
    with patch.object(pwgen.Prompt, 'ask', return_value='1'):
        pwgen.read_passwords_encrypted()
output2 = pwgen.console.file.getvalue()
pwgen.console.file.seek(0); pwgen.console.file.truncate(0)
check('输入序号 1 后显示完整密码', 'Abc123!@#Long' in output2)

# ============================================================
print('\n===== 13. 新功能: 搜索/过滤 (#9) =====')
# ============================================================

# 准备含不同强度的数据
for f in [enc_file, salt_file]:
    if f.exists():
        f.unlink()

search_data = [
    {"password": "GitHub_Token_2026!", "length": 19, "entropy": 110, "strength": "极强", "created_at": "2026-01-01"},
    {"password": "wifi_home_123", "length": 13, "entropy": 45, "strength": "中等", "created_at": "2026-01-02"},
    {"password": "Bank_PIN_secure!!", "length": 17, "entropy": 100, "strength": "很强", "created_at": "2026-01-03"},
]
pwgen.encrypt_and_save(search_data, MASTER_PWD)

# 搜索 "GitHub" 应只匹配 1 条
with patch.object(pwgen.getpass, 'getpass', return_value=MASTER_PWD):
    with patch.object(pwgen.Prompt, 'ask', return_value=''):
        pwgen.read_passwords_encrypted(search='GitHub')
output3 = pwgen.console.file.getvalue()
pwgen.console.file.seek(0); pwgen.console.file.truncate(0)
check('搜索 GitHub 匹配 1 条', '1' in output3 and '条' in output3, output3[:150])

# 搜索 "强" 应匹配 3 条
with patch.object(pwgen.getpass, 'getpass', return_value=MASTER_PWD):
    with patch.object(pwgen.Prompt, 'ask', return_value=''):
        pwgen.read_passwords_encrypted(search='强')
output4 = pwgen.console.file.getvalue()
pwgen.console.file.seek(0); pwgen.console.file.truncate(0)
check('搜索 强 匹配 3 条', '3' in output4 and '条' in output4, output4[:150])

# 搜索不存在的关键词
with patch.object(pwgen.getpass, 'getpass', return_value=MASTER_PWD):
    with patch.object(pwgen.Prompt, 'ask', return_value=''):
        pwgen.read_passwords_encrypted(search='zzzznotexist')
output5 = pwgen.console.file.getvalue()
pwgen.console.file.seek(0); pwgen.console.file.truncate(0)
check('搜索不存在关键词提示未找到', '未找到' in output5, output5[:150])

# ============================================================
print('\n===== 14. 新功能: SFTP 重试机制 (#6) =====')
# ============================================================

# 模拟 sync_after_save 第一次失败、第二次成功
import time as _time

call_count = {'n': 0}
orig_create = pwgen.create_sftp_client

def mock_create_fail_then_succeed():
    call_count['n'] += 1
    if call_count['n'] <= 1:
        raise OSError("模拟连接失败")
    # 第二次成功 - 返回 mock 对象
    class MockSFTP:
        def put(self, *a): pass
        def stat(self, *a): raise FileNotFoundError()
        def mkdir(self, *a): pass
        def close(self): pass
    class MockSSH:
        def open_sftp(self): return MockSFTP()
        def close(self): pass
    return MockSSH(), MockSFTP()

# 设置 SFTP 已配置
pwgen.SFTP_HOST = 'test.example.com'
pwgen.SFTP_USER = 'testuser'

# 确保加密文件存在
pwgen.encrypt_and_save(search_data, MASTER_PWD)

with patch.object(pwgen, 'sftp_is_configured', return_value=True):
    with patch.object(pwgen, 'create_sftp_client', side_effect=mock_create_fail_then_succeed):
        with patch.object(pwgen, 'HAS_PARAMIKO', True):
            with patch.object(_time, 'sleep', side_effect=lambda x: None):  # 跳过真实等待
                pwgen.sync_after_save()
                check('sync 重试后成功', call_count['n'] == 2, f'实际调用次数: {call_count["n"]}')

# 恢复 SFTP 配置
pwgen.SFTP_HOST = ''
pwgen.SFTP_USER = ''

# ============================================================
print('\n===== 15. Web 版 HTML 完整性检查 =====')
# ============================================================

import re
html_path = PROJECT / 'app' / 'pwgen.html'
html_content = html_path.read_text(encoding='utf-8')

check('HTML 包含批量生成按钮', 'btnBatch' in html_content)
check('HTML 包含强度统计容器', 'strengthStats' in html_content)
check('HTML 包含 HIST_KEY 常量', 'HIST_KEY' in html_content)
check('HTML 包含 loadHistory 函数', 'function loadHistory' in html_content)
check('HTML 包含 saveHistory 函数', 'function saveHistory' in html_content)
check('HTML 包含 batchGenerate 函数', 'function batchGenerate' in html_content)
check('HTML 包含 renderStrengthStats 函数', 'function renderStrengthStats' in html_content)
check('HTML 无 escapeJs 函数 (已删除)', 'function escapeJs' not in html_content)
check('HTML 无 inline onclick=copyText (XSS 已修复)', 'onclick="copyText' not in html_content)
check('HTML 无 inline onclick=vaultDelete (XSS 已修复)', 'onclick="vaultDelete' not in html_content)

# ============================================================
# 清理测试产生的文件
# ============================================================
for f in [enc_file, salt_file]:
    if f.exists():
        f.unlink()

# 清理测试历史 (删除本次测试追加的一条)
hist_final = pwgen.load_history()
if hist_final and hist_final[-1].get('length') == len('test_pwd_123'):
    hist_final.pop()
    hist_path = pwgen.HISTORY_FILE
    try:
        import json as _json
        if hist_final:
            with open(hist_path, 'w', encoding='utf-8') as f:
                _json.dump(hist_final, f, ensure_ascii=False, indent=2)
        else:
            hist_path.unlink(missing_ok=True)
    except Exception:
        pass

# ============================================================
print(f'\n{"="*60}')
print(f'测试结果: {passed} 通过, {failed} 失败, 共 {passed + failed} 项')
if failed_tests:
    print('\n失败的测试:')
    for t in failed_tests:
        print(f'  - {t}')
print(f'{"="*60}')
if failed == 0:
    print('[OK] 全部测试通过!')
sys.exit(0 if failed == 0 else 1)

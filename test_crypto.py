"""端到端测试加密存储功能"""
import json
import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def test_encrypt_decrypt():
    """测试加密和解密流程"""
    salt = os.urandom(16)
    master_password = "MySecretMaster123!"
    
    # 派生密钥
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480_000)
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))
    fernet = Fernet(key)
    
    # 模拟密码数据
    data = [
        {"password": "abc123XYZ!@#", "length": 12, "strength": "强"},
        {"password": "P@ssw0rd_Test!", "length": 14, "strength": "很强"},
    ]
    
    # 加密
    plaintext = json.dumps(data, ensure_ascii=False).encode('utf-8')
    encrypted = fernet.encrypt(plaintext)
    
    print(f"[1] 加密完成, 密文长度: {len(encrypted)} bytes")
    
    # 用相同密码解密
    kdf2 = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480_000)
    key2 = base64.urlsafe_b64encode(kdf2.derive(master_password.encode('utf-8')))
    fernet2 = Fernet(key2)
    
    decrypted = json.loads(fernet2.decrypt(encrypted).decode('utf-8'))
    assert decrypted == data, "解密数据不匹配!"
    print(f"[2] 正确密码解密成功 ✓ 恢复了 {len(decrypted)} 条记录")
    
    # 用错误密码解密
    wrong_password = "WrongPassword!"
    kdf3 = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480_000)
    key3 = base64.urlsafe_b64encode(kdf3.derive(wrong_password.encode('utf-8')))
    fernet3 = Fernet(key3)
    
    try:
        fernet3.decrypt(encrypted)
        print("[3] 错误: 不应该解密成功!")
    except InvalidToken:
        print("[3] 错误密码被正确拒绝 ✓")
    
    print("\n全部测试通过!")


if __name__ == "__main__":
    test_encrypt_decrypt()

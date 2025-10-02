"""
配置加密工具模块
使用Fernet对称加密保护敏感配置信息（如API Key）
"""
from cryptography.fernet import Fernet
from flask import current_app
import base64
import hashlib


class ConfigEncryption:
    """配置加密/解密工具类"""

    @staticmethod
    def _get_encryption_key() -> bytes:
        """
        基于应用SECRET_KEY生成加密密钥
        确保密钥在应用重启后保持一致
        """
        secret = current_app.config.get('SECRET_KEY', 'dev-secret-key')
        # 使用SHA256生成32字节密钥，然后Base64编码为Fernet格式
        key_bytes = hashlib.sha256(secret.encode()).digest()
        return base64.urlsafe_b64encode(key_bytes)

    @staticmethod
    def encrypt(plain_text: str) -> str:
        """
        加密字符串

        Args:
            plain_text: 明文字符串

        Returns:
            加密后的Base64编码字符串
        """
        if not plain_text:
            return ''

        key = ConfigEncryption._get_encryption_key()
        fernet = Fernet(key)
        encrypted_bytes = fernet.encrypt(plain_text.encode())
        return encrypted_bytes.decode()

    @staticmethod
    def decrypt(encrypted_text: str) -> str:
        """
        解密字符串

        Args:
            encrypted_text: 加密的Base64编码字符串

        Returns:
            解密后的明文字符串
        """
        if not encrypted_text:
            return ''

        try:
            key = ConfigEncryption._get_encryption_key()
            fernet = Fernet(key)
            decrypted_bytes = fernet.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            current_app.logger.error(f"解密失败: {str(e)}")
            return ''

    @staticmethod
    def mask_api_key(api_key: str, show_chars: int = 4) -> str:
        """
        脱敏显示API Key

        Args:
            api_key: 完整API Key
            show_chars: 前后各显示的字符数

        Returns:
            脱敏后的API Key，格式如 "hk-abcd****...****xyz1"
        """
        if not api_key or len(api_key) <= show_chars * 2:
            return api_key

        prefix = api_key[:show_chars]
        suffix = api_key[-show_chars:]
        return f"{prefix}****...****{suffix}"
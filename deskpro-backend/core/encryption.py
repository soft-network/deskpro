"""
Field-level encryption using Fernet symmetric encryption.

Used to protect sensitive credentials at rest in the control-plane DB
(e.g. Neon DB passwords stored on the Tenant model).

Key is loaded from FIELD_ENCRYPTION_KEY in settings — generate once with:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""
from cryptography.fernet import Fernet
from django.conf import settings


def get_fernet() -> Fernet:
    return Fernet(settings.FIELD_ENCRYPTION_KEY.encode())


def encrypt(plaintext: str) -> str:
    """Encrypt a plaintext string; returns base64-encoded ciphertext."""
    return get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt Fernet ciphertext back to plaintext."""
    return get_fernet().decrypt(ciphertext.encode()).decode()

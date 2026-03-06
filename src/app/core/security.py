from cryptography.fernet import Fernet
from src.app.core.config import settings

# In a real app, this key should be in settings/env
SECRET_KEY = Fernet.generate_key()
fernet = Fernet(SECRET_KEY)

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

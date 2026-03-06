from src.app.core.security import encrypt_data, decrypt_data

def test_encryption_decryption():
    original_data = "This is a secret message"
    encrypted = encrypt_data(original_data)
    assert encrypted != original_data
    
    decrypted = decrypt_data(encrypted)
    assert decrypted == original_data

# app/utils/encryptor.py

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_file(file_path):
    """
    Encrypts the file using AES-256.
    Returns the path to the encrypted file and the encryption key.
    """
    key = get_random_bytes(32)  # 256-bit key
    cipher = AES.new(key, AES.MODE_EAX)

    with open(file_path, 'rb') as f:
        plaintext = f.read()

    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    encrypted_path = file_path + ".enc"
    with open(encrypted_path, 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)

    return encrypted_path, key

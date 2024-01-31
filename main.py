from getpass import getpass
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os

FILE_NAME = "passwords"
KEY_FILE_NAME = "key.key"
accounts = {}

def get_key_from_password(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encrypt(key, data_to_encrypt):
    f = Fernet(key)
    encrypted_data = f.encrypt(data_to_encrypt)
    save_file(encrypted_data)

def decrypt(key):
    f = Fernet(key)
    file_data = open_file()
    decrypted_data = f.decrypt(file_data)
    return decrypted_data

def open_file():
    try:
        with open(FILE_NAME, "rb") as file:
            file_data = file.read()
    except FileNotFoundError:
        print("File not found, creating new file...")
        with open(FILE_NAME, "wb") as file:
            file_data = b''
    return file_data

def save_file(data):
    try:
        with open(FILE_NAME, "wb") as file:
            file.write(data)
    except FileNotFoundError:
        with open(FILE_NAME, "wb") as file:
            file.write(data)

def get_salt():
    try:
        with open(KEY_FILE_NAME, "rb") as file:
            salt = file.read()
    except FileNotFoundError:
        print("File not found, creating new file...")
        with open(KEY_FILE_NAME, "wb") as file:
            salt = os.urandom(16)
            file.write(salt)
    return salt

def init():
    password = getpass("Enter password: ").encode()
    salt = get_salt()

    key = get_key_from_password(password, salt)

    print(decrypt(key))

if __name__ == "__main__":
    init()

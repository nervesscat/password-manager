from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidSignature
from getpass import getpass
import base64
import os
import hashlib

__ACCOUNTS_FILE_NAME = "passwords"
__KEY_FILE_NAME = "salt.key"
__PASSWORD_HASH_FILE_NAME = "password_hash"

class HashNotFoundError(FileNotFoundError):
    """Raised when the hash is not found"""
    pass

class SaltNotFoundError(FileNotFoundError):
    """Raised when the salt is not found"""
    pass

class EncryptedDataNotFoundError(FileNotFoundError):
    """Raised when the encrypted data is not found"""
    pass

def get_key_from_password(password : bytes, salt : bytes) -> bytes:
    """
    Generates a key from a password and a salt    
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encrypt(key : bytes, data_to_encrypt : str) -> bytes:
    """
    Encrypts data using a key
    """
    f = Fernet(key)
    encrypted_data = f.encrypt(str(data_to_encrypt).encode())
    return encrypted_data

def decrypt(key : bytes, data_to_decrypt : bytes) -> bytes:
    """
    Decrypts data using a key
    """
    f = Fernet(key)
    decrypted_data = f.decrypt(data_to_decrypt)
    return decrypted_data.decode()

def open_file(file_name : str) -> bytes:
    """
    Opens a file and returns its content
    """
    with open(file_name, "rb") as file:
        file_data = file.read()
        return file_data

def save_file(file_name : str, data : bytes) -> None:
    """
    Saves data to a file
    """
    with open(file_name, "wb") as file:
        file.write(data)

def save_salt() -> None:
    """
    Saves a salt to a file
    """
    salt = os.urandom(16)
    save_file(__KEY_FILE_NAME, salt)


def get_salt() -> bytes:
    """
    Gets a salt from a file
    """
    try:
        return open_file(__KEY_FILE_NAME)
    except FileNotFoundError:
        raise SaltNotFoundError("The salt was not found in the system files")

def save_password_hash(password : str) -> None:
    """
    Saves a hash of the password to a file
    """
    password_hash = hash_password(password.encode())
    save_file(__PASSWORD_HASH_FILE_NAME, password_hash)

def get_password_hash() -> bytes:
    """
    Gets a password hash from a file
    """
    try:
        return open_file(__PASSWORD_HASH_FILE_NAME)
    except FileNotFoundError:
        raise HashNotFoundError("The hash was not found in the system files")

def hash_password(password : bytes) -> bytes:
    """
    Hashes a password
    """
    return hashlib.sha256(password).digest()

def save_encrypted_file(data : bytes) -> None:
    """
    Saves encrypted data to a file
    """
    try:
        save_file(__ACCOUNTS_FILE_NAME, data)
    except FileNotFoundError:
        raise EncryptedDataNotFoundError("The encrypted data was not found in the system files")
    
def get_encrypted_file() -> bytes:
    """
    Gets encrypted data from a file
    """
    try:
        return open_file(__ACCOUNTS_FILE_NAME)
    except FileNotFoundError:
        raise EncryptedDataNotFoundError("The encrypted data was not found in the system files")

def verify_password(password : bytes) -> bool:
    """
    Verifies a password against the stored password hash
    """
    try:
        stored_password_hash = open_file(__PASSWORD_HASH_FILE_NAME)
        password_hash = hash_password(password)
        return password_hash == stored_password_hash
    except FileNotFoundError:
        raise HashNotFoundError("The hash was not found in the system files")

def check_password_file_exists() -> None:
    """
    Checks if the password hash file exists, if it doesn't it will create it
    """
    if not os.path.isfile(__PASSWORD_HASH_FILE_NAME):
        print("Is it your first time?\nNo password found, please create a password")
        password = getpass("Enter password: ")
        print("Type the password again to confirm")
        password_confirmation = getpass("Enter password: ")
        if password == password_confirmation:
            save_password_hash(password)
            save_salt()
            print("Password created successfully")
        else:
            print("Passwords do not match, please try again")
            check_password_file_exists()
    else:
        return

def encrypt_and_save_data(data : str) -> bytes:
    """
    Encrypts data and saves it to a file 
    """
    try:
        salt = get_salt()
        password = getpass("Enter password: ").encode()
        if not verify_password(password):
            print("Incorrect password")
            return
        key = get_key_from_password(password, salt)
        encrypted_data = encrypt(key, data)
        save_encrypted_file(encrypted_data)
        return encrypted_data
    except InvalidSignature:
        raise InvalidSignature("The password is incorrect")
    except SaltNotFoundError:
        check_password_file_exists()
        encrypt_and_save_data(data)

def get_decrypt_data() -> str:
    """
    Decrypts data from a file
    """
    if not os.path.isfile(__ACCOUNTS_FILE_NAME):
        print("Encrypted data not found")
        raise EncryptedDataNotFoundError("The encrypted data was not found in the system files")

    try:
        salt = get_salt()
        password = getpass("Enter password: ").encode()
        if not verify_password(password):
            print("Incorrect password")
            raise InvalidSignature("The password is incorrect")
        key = get_key_from_password(password, salt)
        file_data = get_encrypted_file()
        decrypted_data = decrypt(key, file_data)
        return decrypted_data
    except InvalidSignature:
        raise InvalidSignature("The password is incorrect")
    
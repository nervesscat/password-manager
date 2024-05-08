from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidSignature
from getpass import getpass
import base64
import os
import hashlib

__home_dir = os.path.expanduser("~")
__script_dir = os.path.join(__home_dir, ".password_manager")
__ACCOUNTS_FILE_NAME = "passwords"
__KEY_FILE_NAME = "salt.key"
__PASSWORD_HASH_FILE_NAME = "password_hash"

class HashNotFoundError(FileNotFoundError):
    pass

class SaltNotFoundError(FileNotFoundError):
    pass

class EncryptedDataNotFoundError(FileNotFoundError):
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
    f = Fernet(key)
    encrypted_data = f.encrypt(str(data_to_encrypt).encode())
    return encrypted_data

def open_file(file_name : str) -> bytes:
    with open(os.path.join(__script_dir, file_name), "rb") as file:
        file_data = file.read()
        return file_data

def save_file(file_name : str, data : bytes) -> None:
    os.makedirs(__script_dir, exist_ok=True)
    with open(os.path.join(__script_dir, file_name), "wb") as file:
        file.write(data)

def save_salt() -> None:
    salt = os.urandom(16)
    save_file(__KEY_FILE_NAME, salt)


def get_salt() -> bytes:
    try:
        return open_file(__KEY_FILE_NAME)
    except FileNotFoundError:
        raise SaltNotFoundError("The salt was not found in the system files")

def save_password_hash(password : str) -> None:
    password_hash = hash_password(password.encode())
    save_file(__PASSWORD_HASH_FILE_NAME, password_hash)

def get_password_hash() -> bytes:
    try:
        return open_file(__PASSWORD_HASH_FILE_NAME)
    except FileNotFoundError:
        raise HashNotFoundError("The hash was not found in the system files")

def hash_password(password : bytes) -> bytes:
    return hashlib.sha256(password).digest()

def save_encrypted_file(data : bytes) -> None:
    try:
        save_file(__ACCOUNTS_FILE_NAME, data)
    except FileNotFoundError:
        raise EncryptedDataNotFoundError("The encrypted data was not found in the system files")
    
def get_encrypted_file() -> bytes:
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
    if not os.path.isfile(os.path.join(__script_dir, __PASSWORD_HASH_FILE_NAME)):
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
    
def authenticate_user() -> tuple[bool, bytes]:
    try:
        check_password_file_exists()
        password = getpass("Enter password: ").encode()
        if verify_password(password):
            return True, password
        else:
            return False, password
    except HashNotFoundError:
        raise HashNotFoundError("The hash was not found in the system files")

def encrypt_and_save_data(data : str, password : str = None) -> bytes:
    try:
        if password and verify_password(password.encode()):
            return encrypt_data_from_file(password.encode(), data)
        
        is_authenticated, password_bytes = authenticate_user()
        if is_authenticated:
            return encrypt_data_from_file(password_bytes, data)
        raise InvalidSignature("The password is incorrect")
    except SaltNotFoundError:
        check_password_file_exists()

def encrypt_data_from_file(password : bytes, data : str) -> bytes:
    key = get_key_from_password(password, get_salt())
    encrypted_data = encrypt(key, data)
    save_encrypted_file(encrypted_data)
    return encrypted_data

def get_decrypt_data(password : str = None) -> str:
    """
    Decrypts data from a file
    """
    try:
        if password and verify_password(password.encode()): 
            return decrypt_from_files(password.encode())        

        is_authenticated, password_bytes = authenticate_user()
        if is_authenticated:
            return decrypt_from_files(password_bytes)
        raise InvalidSignature("The password is incorrect")
    except EncryptedDataNotFoundError:
        raise EncryptedDataNotFoundError("The encrypted data was not found in the system files")
    
def decrypt_from_files(password : bytes) -> str:
    key = get_key_from_password(password, get_salt())
    file_data = get_encrypted_file()
    decrypted_data = decrypt(key, file_data)
    return decrypted_data
    
def decrypt(key : bytes, data_to_decrypt : bytes) -> str:
    f = Fernet(key)
    decrypted_data = f.decrypt(data_to_decrypt)
    return decrypted_data.decode()
from getpass import getpass
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidKey, InvalidSignature

import base64
import os
import pyperclip

import argparse

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
    if not os.path.isfile(FILE_NAME):
        encrypt(key, str(accounts).encode())
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

def add_account():
    account_key = input("Enter account website (w/o spaces, .com, etc): ")
    
    username = input("Enter username: ")
    password = input("Enter password: ")
    email = input("Enter email: ")
    
    account = {
        "username": username,
        "password": password,
        "email": email
    }

    if account_key in accounts:
        accounts[account_key].append(account)
    else:    
        accounts[account_key] = [account]

    print("Account added successfully")

def get_account(account_key=None):
    if not account_key:
        account_key = input("Enter account website (w/o spaces, .com, etc): ")

    if account_key in accounts and accounts[account_key].__len__() > 1:
        enumerate_all_accounts(account_key)

        choice = input("Enter account number: ")
        print("\033[92musername:\033[0m", accounts[account_key][int(choice)-1]["username"])
        print("\033[92memail:\033[0m", accounts[account_key][int(choice)-1]["email"])

        pyperclip.copy(accounts[account_key][int(choice)-1]["password"])
        print("Password copied to clipboard")
    elif account_key in accounts:
        enumerate_single_account(account_key)

        pyperclip.copy(accounts[account_key][0]["password"])
        print("Password copied to clipboard")
    else:
        print("Account not found")

def enumerate_all_accounts(account_key):
    for i, account in enumerate(accounts[account_key]):
        print(f"\033[92m\nAccount {i+1}:\033[0m")
        print("\033[92musername:\033[0m", account["username"])
        print("\033[92memail:\033[0m", account["email"])    

def enumerate_single_account(account_key):
    print("\033[92musername:\033[0m", accounts[account_key][0]["username"])
    print("\033[92memail:\033[0m", accounts[account_key][0]["email"])

def delete_account():
    account_key = input("Enter account website (w/o spaces, .com, etc): ")
    if account_key in accounts and accounts[account_key].__len__() > 1:
        enumerate_all_accounts(account_key)

        choice = input("Enter account number: ")
        del accounts[account_key][int(choice)-1]
        print("Account deleted successfully")

    elif account_key in accounts:
        enumerate_single_account(account_key)
        print("Are you sure you want to delete this account? (y/n)")
        choice = input("Enter choice: ")

        if choice == "y":
            del accounts[account_key]
            print("Account deleted successfully")
        else:
            print("Account not deleted")

    else:
        print("Account not found")

def delete_all_data():
    print("Are you sure you want to delete all data? (y/n)")
    choice = input("Enter choice: ")

    if choice == "y":
        accounts = {}
        print("All data deleted successfully")
    else:
        print("Data not deleted")

def authenticate():
    try:
        password = getpass("Enter password: ").encode()
        salt = get_salt()

        key = get_key_from_password(password, salt)

        raw_data = decrypt(key)

        if raw_data:
            global accounts
            accounts = eval(raw_data.decode())
    except InvalidKey or InvalidSignature:
        print("\033[91mInvalid password!!\033[0m")
        authenticate()
    except InvalidToken:
        print("\033[91mInvalid token!!\033[0m")
        authenticate()
    return key

def init():
    while True:
        print("1. Add account")
        print("2. Get account")
        print("3. Show all accounts")
        print("\033[93m4. Delete account\033[0m")
        print("\033[91m5. Delete All Data\033[0m")
        print("6. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            add_account()
            pass
        elif choice == "2":
            get_account()
            pass
        elif choice == "3":
            print(accounts)
        elif choice == "4":
            delete_account()
            pass
        elif choice == "5":
            delete_all_data()
        elif choice == "6":
            break
        else:
            print("Invalid choice")

def init_args_parser():
    parser = argparse.ArgumentParser(description="A simple password manager")
    parser.add_argument("-i", "--init", help="Initialize the password manager", action="store_true")
    parser.add_argument("-g", "--get", help="Get password for an account <website>", type=str)
    parser.add_argument("-a", "--add", help="Add password for an account", action="store_true")
    parser.add_argument("-d", "--delete", help="Delete password for an account", action="store_true")
    parser.add_argument("-s", "--show", help="Show all accounts", action="store_true")

    return parser.parse_args()

if __name__ == "__main__":
    args = init_args_parser()

    try:
        key = authenticate()
        
        if not any(vars(args).values()):
            init()
        else:
            if args.get:
                get_account(args.get)
            elif args.add:
                add_account()
            elif args.delete:
                delete_account()
            elif args.show:
                print(accounts)
            encrypt(key, str(accounts).encode())
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        encrypt(key, str(accounts).encode())

    
        

from encrypt import get_decrypt_data, encrypt_and_save_data, InvalidSignature
import csv
import json

class MapManager:
    def __init__(self, password : str = None):
        self.password = password
        self._map = {}
        self.load_map()

    def load_map(self) -> None:
        try:
            encrypted_data = get_decrypt_data(self.password)
            self._map = json.loads(encrypted_data)
        except InvalidSignature:
            raise InvalidSignature("The password is incorrect")
        except Exception as e:
            print(f"Failed to load map: {e}")
            self._map = {}

    def save_map(self) -> None:
        try:
            encrypted_data = json.dumps(self._map, indent=4)
            encrypt_and_save_data(encrypted_data, self.password)
        except InvalidSignature:
            print("The password is incorrect")
            encrypt_and_save_data(encrypted_data)
        except Exception as e:
            print(f"Failed to save map: {e}")

    def get_map(self) -> dict:
        return self._map

    def update_map(self, new_map : dict) -> None:
        self._map = new_map
        self.save_map()
    
    def reset_map(self) -> None:
        self._map = {}
        self.save_map()

from fuzzywuzzy import process, fuzz
from pyperclip import copy
import json

class AccountManager:
    def __init__(self, map_manager):
        self.map_manager = map_manager

    def load_map_from_csv(self, file : str, username_col = 1, password_col = 2, website_col = 5) -> None:
        new_map = self.map_manager.get_map()
        with open(file, mode="r") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                website = row[website_col]
                username = row[username_col]
                password = row[password_col]
                if website not in new_map:
                    new_map[website] = []
                account = {"username": username, "password": password}
                if account not in new_map[website] and username not in [account["username"] for account in new_map[website]]:
                    new_map[website].append(account)
        self.map_manager.update_map(new_map)

    def add_account(self, website : str, username : str, password : str) -> None:
        map_data = self.map_manager.get_map()
        if website not in map_data:
            map_data[website] = []
        account = {"username": username, "password": password}
        if account not in map_data[website] and username not in [account["username"] for account in map_data[website]]:
            map_data[website].append(account)
        self.map_manager.update_map(map_data)

    def remove_account(self, website : str, username : str) -> None:
        map_data = self.map_manager.get_map()
        if website in map_data:
            map_data[website] = [account for account in map_data[website] if account["username"] != username]
            if not map_data[website]:
                del map_data[website]
            self.map_manager.update_map(map_data)

    def get_accounts_by_website(self, website : str) -> list:
        map_data = self.map_manager.get_map()
        return map_data.get(website, [])
        
    def search_website_fuzzy(self, search_key : str) -> str:
        map_data = self.map_manager.get_map()
        best_match = process.extractOne(search_key, map_data.keys(), scorer=fuzz.token_sort_ratio)
        return best_match[0] if best_match and best_match[1] >= 70 else search_key

    def copy_password_to_clipboard(self, website : str, username : str) -> bool:
        password = self.get_password_by_username(website, username)
        if password:
            copy(password)
            print("Password copied to clipboard")
            return True
        print("Password not found")
        return False
    
    def get_password_by_username(self, website : str, username: str) -> str | None:
        accounts = self.get_accounts_by_website(website)
        account = next((item for item in accounts if item["username"] == username), None)
        return account["password"] if account else None

    def search_websites_matches_fuzzy(self, search_key : str) -> list:
        map_data = self.map_manager.get_map()
        matches = process.extract(search_key, map_data.keys(), limit=5)
        return [match[0] for match in matches]
    
    def modify_password(self, website : str, username : str, new_password : str) -> None:
        map_data = self.map_manager.get_map()
        accounts = map_data.get(website, [])
        for account in accounts:
            if account["username"] == username:
                account["password"] = new_password
                break
        self.map_manager.update_map(map_data)
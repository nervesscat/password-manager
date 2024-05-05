from json import JSONDecodeError, loads, dumps
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from encrypt import get_decrypt_data, encrypt_and_save_data, InvalidSignature, EncryptedDataNotFoundError
from pyperclip import copy

import csv

#! This should  be separated into different classes, one for the map and one for the account handler
class MapHandler:
    __isAltered = False

    def __init__(self):
        try:
            self.__isAltered = False
            self.parse_map(get_decrypt_data())
        except InvalidSignature:
            print("Data could not be decrypted")
            raise InvalidSignature("The password is incorrect")
        except EncryptedDataNotFoundError:
            print("No data found, creating a new map")
            self.map = {}
        
    def parse_map(self, map : str) -> None:
        try:
            self.map = loads(map)
        except JSONDecodeError:
            print("The map is invalid, creating a new one")
            self.map = {}

    def parse_csv(self, file : str, username_col = 1, password_col = 2, website_col = 5) -> None:
        with open(file, mode="r") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                self.add_user_to_map(row[website_col], row[username_col], row[password_col])
        
    def get_map(self) -> dict:
        return self.map

    def add_user_by_searching(self, key: str, username: str, password: str) -> None:
        """
        Adds a user to the map first by searching if the key exists
        """
        if key in self.map:
            self.add_user_to_map(key, username, password)
            return

        find_key = self.search_dict_fuzzy(key)
        response = self.get_user_confirmation(key)

        if response:
            self.add_user_to_map(find_key, username, password)
        else:
            self.add_user_to_map(key, username, password)

    def get_user_confirmation(self, key: str) -> bool:
        """
        Asks the user for confirmation and returns True if the user confirms, False otherwise
        """
        response = input(f"Would you want to say {key} is the website you want to add/delete the user to? (y/n)")
        return response.lower() == "y"

    def add_user_to_map(self, key : str, username : str, password : str) -> dict:
        self.create_new_key(key)
        self.append_to_existing_key(key, username, password)
        return self.map

    def create_new_key(self, key : str) -> dict:
        if key in self.map:
            return
        self.__isAltered = True
        self.map[key] = []
        return self.map

    def append_to_existing_key(self, key : str, username : str, password : str) -> dict:
        if key not in self.map or any(user["username"] == username for user in self.map[key]):
            print("No website/user found")
            return
        
        self.__isAltered = True
        self.map[key].append({
            "username": username,
            "password": password
        })

        return self.map

    def remove_key_from_map(self, key : str) -> dict:
        if key not in self.map:
            print("No website found")
            return
        
        self.__isAltered = True
        response = self.get_user_confirmation(key)
        if response: self.map.pop(key)
        return self.map

    def remove_user_by_searching(self, key : str, username : str) -> dict:
        """
        Removes a user from the map by searching
        """
        find_key = self.search_dict_fuzzy(key)
        if key == find_key:
            self.remove_user_from_map(key, username)
            return self.map
        
        response = input(f"Would you want to say {find_key} is the website you want to remove the user from? (y/n)")
        if response.lower() == "y":
            self.remove_user_from_map(find_key, username)
        return self.map

    def remove_user_from_map(self, key : str, username : str) -> dict:
        if key not in self.map or not any(user["username"] == username for user in self.map[key]):
            print("No website/user found")
            return self.map
        
        self.__isAltered = True
        self.map[key] = [user for user in self.map[key] if user["username"] != username]
        return self.map

    def erase_and_save_map(self) -> dict:
        response = input("Are you sure you want all the data? (y/n): ")
        if response.lower == "y":
            self.erase_map()
            self.save_map()
        return self.map

    def erase_map(self) -> dict:
        self.map = {}
        self.__isAltered = True
        return self.map

    def save_map(self) -> None:
        """
        Saves the map using __repr__ return
        """
        if not self.__isAltered:
            return
        self.__isAltered = False
        encrypt_and_save_data(self)

    def get_value_from_map(self, key : str) -> str:
        return self.map[key]

    def search_for_keys_and_print_users(self, key : str) -> str:
        key = self.search_dict_fuzzy(key)
        if not key: return None
        list = self.map[key]
        index = self.print_options(list)
        copy(list[index]["password"])
        return list[index]["password"]

    def print_options(self, list: list) -> int:
        for i, account in enumerate(list, start=1):
            print(f"{i}. Username: \033[92m{account['username']}\033[0m")
        print(f"\033[93mEnter the number of the account you want to access\033[0m")
        choice = int(input("Enter choice: "))
        return choice-1
    
    def get_all_users_from_website(self, key : str) -> list:
        key = self.search_dict_fuzzy(key)
        if not key: return None
        return self.map[key]

    def get_password_by_username(self, key : str, username : str) -> str | None:
        password = [user["password"] for user in self.map[key] if user["username"] == username][0]
        if not password:
            return None
        
        copy(password)
        return password
    
    def search_dict_fuzzy(self, key : str) -> tuple | None:
        """
        Searches the map for a key and return a key that is similar
        """
        try:
            return process.extractOne(key, self.map.keys(), scorer=fuzz.token_sort_ratio)[0]
        except TypeError:
            return None
    
    def __repr__(self) -> str:
        return dumps(self.map, indent=4)
from map_handler import AccountManager, MapManager, InvalidSignature
from pyperclip import copy
import secrets
import string

class ManagerFuncs:
    def __init__(self, password) -> None:
        self.map_manager = MapManager(password)
        self.account_manager = AccountManager(self.map_manager)

    def search_accounts(self, website : str) -> dict | None:
        """
            Search for accounts in a website and return the account
        """
        accounts_list = self.account_manager.get_accounts_by_website(website)
        if not accounts_list: return None
        choice = self.__print_users_list_and_choice(accounts_list)
        if 0 <= choice < len(accounts_list): return accounts_list[choice]
        elif choice == len(accounts_list): return None
        else: 
            print("\033[91mInvalid account number\033[0m")
            return self.search_accounts(website)
        
    def __print_users_list_and_choice(self, accounts_list : list) -> int:
        print(f"\033[92mAccounts found:\033[0m")
        for i, account in enumerate(accounts_list, start=1):
            print(f"{i}. {account['username']}")
        print(f"{str(len(accounts_list) + 1)}. Cancel")
        return int(input("Enter account number: ")) - 1

    def get_password(self, website : str, username : str) -> None:
        best_match = self.account_manager.search_website_fuzzy(website)
        self.account_manager.copy_password_to_clipboard(best_match, username)

    def add_account(self, website : str, username : str, password : str) -> None:
        best_match = self.account_manager.search_website_fuzzy(website)
        print(f"Did you mean {best_match}? (y/n)")
        choice = input("Enter choice: ").lower()
        if choice == "y": 
            self.account_manager.add_account(best_match, username, password)
        else:
            self.account_manager.add_account(website, username, password)
    
    def erase_account(self, website : str, username : str) -> None:
        best_match = self.account_manager.search_website_fuzzy(website)
        print(f"Do you want to delete {username} from {best_match}? (y/n)")
        choice = input("Enter choice: ").lower()
        if choice == "y": self.account_manager.remove_account(best_match, username) 

    def argument_choice_load(self, filename : str) -> None:
        self.account_manager.load_map_from_csv(filename)

    def erase_all(self) -> None:
        choice = input("Are you sure you want to delete all data? (y/n)")
        if choice.lower() == "y": self.map_manager.reset_map()

    def argument_generate_password(self, length : int) -> None:
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        copy(password)

    def menu_choice_add(self):
        website = input("Enter website: ")
        username = input("Enter username: ")
        password = input("Enter password: ")
        self.add_account(website, username, password)

    def menu_choice_get(self):
        website = input("Enter website: ")
        website = self.search_websites(website)
        if not website: return
        account = self.search_accounts(website)
        if account: copy(account['password'])

    def search_websites(self, website : str) -> str:
        """
            Search for websites and return the website
        """
        websites = self.account_manager.search_websites_matches_fuzzy(website)
        if not websites: return None
        choice = self.__print_websites_list_and_choice(websites)
        if 0 <= choice < len(websites): return websites[choice]
        elif choice == len(websites): return None
        else: 
            print("\033[91mInvalid website number\033[0m")
            return self.search_websites(website)
        
    def __print_websites_list_and_choice(self, websites : list) -> int:
        print("\033[92mWebsites found:\033[0m")
        for i, website in enumerate(websites, start=1):
            print(f"{i}. {website}")
        print(f"{str(len(websites) + 1)}. Cancel")
        return int(input("Enter website number: ")) - 1

    def menu_choice_search(self):
        website = input("Enter website: ")
        website = self.search_websites(website)

    def menu_choice_modify(self):
        website = input("Enter website: ")
        website = self.search_websites(website)
        if not website: return
        account = self.search_accounts(website)
        if not account: return
        new_password = input("Enter new password: ")
        self.account_manager.modify_password(website, account['username'], new_password)

    def menu_choice_delete(self):
        website = input("Enter website: ")
        website = self.search_websites(website)
        if not website: return
        account = self.search_accounts(website)
        if not account: return
        self.erase_account(website, account['username'])
        print(f"\033[93mAre you sure you want to delete this account ({account['username']}) from {website}?\033[0m")
        choice = input("Enter choice (y/n): ").lower()
        if choice == "y": self.account_manager.remove_account(website, account['username'])

    def menu_choice_erase_all(self):
        self.erase_all()

    def menu_choice_load_csv(self):
        filename = input("Enter filename: ")
        csv_cols_order = input("Enter the order of the columns (username, password, website) (default 1, 2, 5): ")
        if csv_cols_order:
            cols = csv_cols_order.split(',')
            self.account_manager.load_map_from_csv(filename, int(cols[0]), int(cols[1]), int(cols[2]))
        else:
            self.account_manager.load_map_from_csv(filename)

    def menu_choice_generate_password(self):
        length = int(input("Enter length of password: "))
        self.argument_generate_password(length)
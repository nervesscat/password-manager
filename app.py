from enum import Enum
from map_handler import AccountManager, MapManager, InvalidSignature
from argparse import ArgumentParser
from getpass import getpass
from pyperclip import copy

# pyinstaller --onefile app.py
# sudo mv dist/app /usr/local/bin/password_manager

def run():
    args = init_args_parser()
    if args.init:
        init()
    elif args.print:
        search_accounts(args.print[0])
    elif args.get:
        get_password(args.get[0], args.get[1])
    elif args.add:
        add_account(args.add[0], args.add[1], args.add[2])
    elif args.erase:
        erase_account(args.erase[0], args.erase[1])
    elif args.load:
        account_manager.load_map_from_csv(args.load[0])
    elif args.reset:
        erase_all()
    elif args.generate_password:
        pass
    else:
        init()

def get_password(website : str, username : str) -> None:
    best_match = account_manager.search_website_fuzzy(website)
    account_manager.copy_password_to_clipboard(best_match, username)

def add_account(website : str, username : str, password : str) -> None:
    best_match = account_manager.search_website_fuzzy(website)
    print(f"Did you mean {best_match}? (y/n)")
    choice = input("Enter choice: ").lower()
    if choice == "y": 
        account_manager.add_account(best_match, username, password)
    else:
        account_manager.add_account(website, username, password)

def erase_account(website : str, username : str) -> None:
    best_match = account_manager.search_website_fuzzy(website)
    print(f"Do you want to delete {username} from {best_match}? (y/n)")
    choice = input("Enter choice: ").lower()
    if choice == "y": account_manager.remove_account(best_match, username)

def erase_all() -> None:
    choice = input("Are you sure you want to delete all data? (y/n)")
    if choice.lower() == "y": map_manager.reset_map()

def init_args_parser():
    parser = ArgumentParser(description="Password manager")
    parser.add_argument("-i", "--init", help="Initialize the password manager", action="store_true")
    parser.add_argument("-pr", "--print", nargs=1, metavar=('website'), help="Print all users from a website", type=str)
    parser.add_argument("-g", "--get", nargs=2, metavar=('website', 'username'), help="Get password for an account", type=str)
    parser.add_argument("-a", "--add", nargs=3, metavar=('website', 'username', 'password'), help="Add password for an account", type=str)
    parser.add_argument("-e", "--erase", nargs=2, metavar=('website', 'username'), help="Erase an account from certain website and user", type=str)
    parser.add_argument("-l", "--load", nargs=1, metavar=('filename'), help="Load a csv file", type=str)
    parser.add_argument("-r", "--reset", help="Reset the map", action="store_true")
    parser.add_argument("-ge", "--generate_password", nargs=1, metavar=('length'), help="Generate a password", type=str)
    return parser.parse_args()

def get_menu_choice():
    print("1. Add account")
    print("2. Get account")
    print("3. Search account")
    print("4. Modify account")
    print("\033[93m5. Delete account\033[0m")
    print("\033[91m6. Delete All Data\033[0m")
    print("7. Load from CSV")
    print("0. Exit")
    choice = input("Enter choice: ")
    return choice

class OPTION(Enum):
    ADD = '1'
    GET = '2'
    SEARCH = '3'
    MODIFY = '4'
    DELETE = '5'
    DELETE_ALL = '6'
    LOAD_CSV = '7'
    EXIT = '0'

def search_websites(website : str) -> str:
    """
        Search for websites and return the website
    """
    websites = account_manager.search_websites_matches_fuzzy(website)
    if not websites: return None
    choice = print_websites_list_and_choice(websites)
    if 0 <= choice < len(websites): return websites[choice]
    elif choice == len(websites): return None
    else: 
        print("\033[91mInvalid website number\033[0m")
        return search_websites(website)

def print_websites_list_and_choice(websites : list) -> int:
    print("\033[92mWebsites found:\033[0m")
    for i, website in enumerate(websites, start=1):
        print(f"{i}. {website}")
    print(f"{str(len(websites) + 1)}. Cancel")
    return int(input("Enter website number: ")) - 1

def search_accounts(website : str) -> dict | None:
    """
        Search for accounts in a website and return the account
    """
    accounts_list = account_manager.get_accounts_by_website(website)
    if not accounts_list: return None
    choice = print_users_list_and_choice(accounts_list)
    if 0 <= choice < len(accounts_list): return accounts_list[choice]
    elif choice == len(accounts_list): return None
    else: 
        print("\033[91mInvalid account number\033[0m")
        return search_accounts(website)
    
def print_users_list_and_choice(accounts_list : list) -> int:
    print(f"\033[92mAccounts found:\033[0m")
    for i, account in enumerate(accounts_list, start=1):
        print(f"{i}. {account['username']}")
    print(f"{str(len(accounts_list) + 1)}. Cancel")
    return int(input("Enter account number: ")) - 1

def init():
    while True:
        choice = get_menu_choice()
        if choice == OPTION.ADD.value:
            website = input("Enter website: ")
            username = input("Enter username: ")
            password = input("Enter password: ")
            add_account(website, username, password)
        elif choice == OPTION.GET.value:
            website = input("Enter website: ")
            website = search_websites(website)
            if not website: continue
            account = search_accounts(website)
            if account: copy(account['password'])
        elif choice == OPTION.SEARCH.value:
            website = input("Enter website: ")
            website = search_websites(website)
        elif choice == OPTION.MODIFY.value:
            website = input("Enter website: ")
            website = search_websites(website)
            if not website: continue
            account = search_accounts(website)
            if not account: continue
            new_password = input("Enter new password: ")
            account_manager.modify_password(website, account['username'], new_password)
        elif choice == OPTION.DELETE.value:
            website = input("Enter website: ")
            website = search_websites(website)
            if not website: continue
            account = search_accounts(website)
            if not account: continue
            print(f"\033[93mAre you sure you want to delete this account ({account['username']}) from {website}?\033[0m")
            choice = input("Enter choice (y/n): ").lower()
            if choice == "y": account_manager.remove_account(website, account['username'])
        elif choice == OPTION.DELETE_ALL.value:
            erase_all()
        elif choice == OPTION.LOAD_CSV.value:
            filename = input("Enter filename: ")
            csv_cols_order = input("Enter the order of the columns (username, password, website) (default 1, 2, 5): ")
            if csv_cols_order:
                cols = csv_cols_order.split(',')
                account_manager.load_map_from_csv(filename, int(cols[0]), int(cols[1]), int(cols[2]))
            else:
                account_manager.load_map_from_csv(filename)
        elif choice == OPTION.EXIT.value:
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    try:
        password = getpass("Enter password: ")
        map_manager = MapManager(password)
        account_manager = AccountManager(map_manager)
        run()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
    except InvalidSignature:
        print("Password is incorrect, please try again")
    finally:
        pass
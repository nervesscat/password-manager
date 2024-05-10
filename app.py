from enum import Enum
from manager_funcs import ManagerFuncs, InvalidSignature
from argparse import ArgumentParser
from getpass import getpass

# pyinstaller --onefile app.py
# sudo mv dist/app /usr/local/bin/password_manager

def run():
    args = init_args_parser()
    if args.init:
        init()
    elif args.print:
        manager_funcs.search_accounts(args.print[0])
    elif args.get:
        manager_funcs.get_password(args.get[0], args.get[1])
    elif args.add:
        manager_funcs.add_account(args.add[0], args.add[1], args.add[2])
    elif args.erase:
        manager_funcs.erase_account(args.erase[0], args.erase[1])
    elif args.load:
        manager_funcs.argument_choice_load(args.load[0])
    elif args.reset:
        manager_funcs.erase_all()
    elif args.generate_password:
        manager_funcs.argument_generate_password(int(args.generate_password[0]))
    else:
        init()

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

class OPTION(Enum):
    ADD = '1'
    GET = '2'
    SEARCH = '3'
    MODIFY = '4'
    DELETE = '5'
    DELETE_ALL = '6'
    LOAD_CSV = '7'
    GENERATE_PASSWORD = '8'
    EXIT = '0'

def get_menu_choice():
    print("1. Add account")
    print("2. Get account")
    print("3. Search account")
    print("4. Modify account")
    print("\033[93m5. Delete account\033[0m")
    print("\033[91m6. Delete All Data\033[0m")
    print("7. Load from CSV")
    print("8. Generate password")
    print("0. Exit")
    choice = input("Enter choice: ")
    return choice

def init():
    while True:
        choice = get_menu_choice()
        if choice == OPTION.ADD.value:
            manager_funcs.menu_choice_add()
        elif choice == OPTION.GET.value:
            manager_funcs.menu_choice_get()
        elif choice == OPTION.SEARCH.value:
            manager_funcs.menu_choice_search()
        elif choice == OPTION.MODIFY.value:
            manager_funcs.menu_choice_modify()
        elif choice == OPTION.DELETE.value:
            manager_funcs.menu_choice_delete()
        elif choice == OPTION.DELETE_ALL.value:
            manager_funcs.erase_all()
        elif choice == OPTION.LOAD_CSV.value:
            manager_funcs.menu_choice_load_csv()
        elif choice == OPTION.GENERATE_PASSWORD.value:
            manager_funcs.menu_choice_generate_password()
        elif choice == OPTION.EXIT.value:
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    try:
        password = getpass("Enter password: ")
        manager_funcs = ManagerFuncs(password)
        run()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
    except InvalidSignature:
        print("Password is incorrect, please try again")
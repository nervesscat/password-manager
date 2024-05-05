from enum import Enum
from encrypt import check_password_file_exists
from map_handler import MapHandler
from argparse import ArgumentParser

class Option(Enum):
    pass

def init():
    args = init_args_parser()
    if args.init:
        pass
    elif args.print:
        users = map_handler.get_all_users_from_website(args.print[0])
        print(users)
    elif args.get:
        if args.get[1] == "all":
            users = map_handler.get_all_users_from_website(args.get[0])
            print(users)
            return
        map_handler.get_password_by_username(args.get[0], args.get[1])
    elif args.add:
        map_handler.add_user_to_map(args.add[0], args.add[1], args.add[2])
    elif args.erase:
        map_handler.remove_user_by_searching(args.erase[0], args.erase[1])
    elif args.load:
        print("Choose the column number for the username, password and website")
        selected_columns = input("Enter the column numbers separated by a comma (1,2,5 by default): ").split(",")
        if len(selected_columns) == 1:
            map_handler.parse_csv(args.load[0])
            return
        map_handler.parse_csv(args.load[0], int(selected_columns[0]), int(selected_columns[1]), int(selected_columns[2]))
    elif args.generate_password:
        print(args.generate_password)
    
    check_password_file_exists()

def init_args_parser():
    parser = ArgumentParser(description="Password manager")
    parser.add_argument("-i", "--init", help="Initialize the password manager", action="store_true")
    parser.add_argument("-pr", "--print", nargs=1, metavar=('website'), help="Print all users from a website", type=str)
    parser.add_argument("-g", "--get", nargs=2, metavar=('website', 'username'), help="Get password for an account", type=str)
    parser.add_argument("-a", "--add", nargs=3, metavar=('website', 'username', 'password'), help="Add password for an account", type=str)
    parser.add_argument("-e", "--erase", nargs=2, metavar=('website', 'username'), help="Erase an account from certain website and user", type=str)
    parser.add_argument("-l", "--load", nargs=1, metavar=('filename'), help="Load a csv file", type=str)
    parser.add_argument("-ge", "--generate_password", nargs=1, metavar=('length'), help="Generate a password", type=str)
    return parser.parse_args()

if __name__ == "__main__":
    map_handler = MapHandler()
    try:
        init()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
    finally:
        map_handler.save_map()
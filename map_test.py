from unittest.mock import patch
from map_handler import AccountManager, MapManager
import unittest

class TestMapHandler(unittest.TestCase):
    __PASSWORD = 'test_password'

    def setUp(self):
        self.map_manager = MapManager(self.__PASSWORD)
        self.account_manager = AccountManager(self.map_manager)

    def tearDown(self):
        self.map_manager.reset_map()

    def test_add_user_to_map(self):
        self.account_manager.add_account('test.com', 'test_user', 'test_password')
        self.assertEqual(self.map_manager.get_map(), {'test.com': [{'username': 'test_user', 'password': 'test_password'}]})

    def test_get_password_by_username(self):
        self.account_manager.add_account('test.com', 'test_user', 'test_password')
        self.assertEqual(self.account_manager.get_password_by_username('test.com', 'test_user'), 'test_password')

    def test_remove_user_by_searching(self):
        self.account_manager.remove_account('test.com', 'test_user')
        self.assertEqual(self.map_manager.get_map(), {})

    def test_get_password_by_null_username(self):
        self.account_manager.remove_account('test.com', 'test_user')
        self.assertEqual(self.account_manager.get_password_by_username('test.com', 'test_user'), None)

    def test_get_all_users_from_website(self):
        self.account_manager.add_account('test.com', 'test_user', 'test_password')
        self.assertEqual(self.account_manager.get_accounts_by_website('test.com'), [{'username': 'test_user', 'password': 'test_password'}])
    
    def test_search_for_keys_and_print_users(self):
        self.account_manager.add_account('test.com', 'test_user', 'test_password')
        self.assertEqual(self.account_manager.search_website_fuzzy('test.c'), 'test.com')

    def test_get_password_by_mispelled_username(self):
        self.account_manager.add_account('test.com', 'test_user', 'test_password')
        self.assertEqual(self.account_manager.get_password_by_username('te.com', 'test_user'), None)

    def test_reset_map(self):
        self.map_manager.reset_map()
        self.assertEqual(self.map_manager.get_map(), {})

    def test_add_and_remove_account(self):
        self.account_manager.add_account('test.com', 'test_user', 'test_password')
        self.account_manager.remove_account('test.com', 'test_user')
        self.assertEqual(self.map_manager.get_map(), {})

if __name__ == '__main__':
    unittest.main()
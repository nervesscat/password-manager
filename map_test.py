from unittest.mock import patch
from map_handler import MapHandler
import unittest
import io

class TestMapHandler(unittest.TestCase):
    def setUp(self):
        self.map_handler = MapHandler()

    #@patch('map_handler.getpass', return_value='test_password')
    def test_add_user_to_map(self):
        self.map_handler.add_user_to_map('test.com', 'test_user', 'test_password')
        self.assertEqual(self.map_handler.get_map(), {'test.com': [{'username': 'test_user', 'password': 'test_password'}]})

    #@patch('map_handler.getpass', return_value='test_password')
    def test_remove_key_from_map(self):
        self.map_handler.add_user_to_map('test.com', 'test_user', 'test_password')
        self.map_handler.remove_key_from_map('test.com')
        self.assertEqual(self.map_handler.get_map(), {})

    #@patch('map_handler.getpass', return_value='test_password')
    def test_remove_user_from_map(self):
        self.map_handler.add_user_to_map('test.com', 'test_user', 'test_password')
        self.map_handler.remove_user_from_map('test.com', 'test_user')
        self.assertEqual(self.map_handler.get_map(), {'test.com': []})

    @patch('builtins.input', side_effect=['y', 'n'])
    def test_erase_map(self, getpass_mock):
        self.map_handler.add_user_to_map('test.com', 'test_user', 'test_password')
        self.map_handler.erase_map()
        self.assertEqual(self.map_handler.get_map(), {})

    #@patch('map_handler.getpass', return_value='test_password')
    def test_get_password_by_username(self):
        self.map_handler.add_user_to_map('test.com', 'test_user', 'test_password')
        password = self.map_handler.get_password_by_username('test.com', 'test_user')
        self.assertEqual(password, 'test_password')

if __name__ == '__main__':
    unittest.main()
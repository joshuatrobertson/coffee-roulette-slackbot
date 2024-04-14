import unittest
from unittest.mock import mock_open, patch
from file_operations import read_reactions


class TestReadReactions(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data="user1,:smile:\nuser2,:heart:\n" * 1000000)
    def test_read_reactions_large_file(self, mock_file):
        # Test reading reactions from a large file with reactions from two users.
        expected_result = {
            'user1': ':smile:',
            'user2': ':heart:'
        }
        result = read_reactions()
        self.assertEqual(len(result), 2)
        self.assertEqual(result, expected_result)

    @patch('builtins.open', new_callable=mock_open, read_data="")
    def test_read_reactions_empty_file(self, mock_file):
        # Test reading reactions from an empty file.
        expected_result = {}
        result = read_reactions()
        self.assertEqual(result, expected_result)

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('builtins.print')
    def test_read_reactions_file_not_found(self, mock_print, mock_file):
        # Test file not found scenario
        result = read_reactions()
        mock_print.assert_called_once_with("No reactions file found.")
        self.assertEqual(result, {})

    @patch('builtins.open', new_callable=mock_open, read_data="user1,:smile:\nuser3,:tea:\nuser1,:smile:")
    def test_reactions_with_duplicates(self, mock_file):
        # Test reading reactions to ensure duplicates are handled correctly (i.e., they are not removed). Although
        # should not occur as it is a dictionary
        expected_result = {
            'user1': ':smile:',
            'user3': ':tea:'
        }
        result = read_reactions()
        self.assertEqual(result, expected_result)

    @patch('builtins.open', new_callable=mock_open, read_data="user1,:smile:\nuser3,:tea:\nuser1,:smile:\n" * 1000)
    def test_read_reactions_large_file_with_duplicates(self, mock_file):
        # Test reading reactions from a large file with duplicates and reactions from two users.
        expected_result = {
            'user1': ':smile:',
            'user3': ':tea:'
        }
        result = read_reactions()
        self.assertEqual(len(result), 2)
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from slack_functions import handle_leftovers


class TestHandleLeftovers(unittest.TestCase):

    @patch('slack_functions.notify_users')  # Patch the notify_users function
    @patch('random.shuffle', lambda x: None)  # Mock shuffle to do nothing for predictability
    def test_pairs_passed_to_notify_users(self, mock_notify):
        users = ['user{}'.format(i) for i in range(21, 1)]  # 20 users, user1 to user20
        expected_pairs = [(users[i], users[i + 1]) for i in range(0, len(users) - 1, 2)]

        handle_leftovers(users)

        mock_notify.assert_called_once_with(expected_pairs)

        called_pairs = mock_notify.call_args[0][0]

        # Verify that all users are paired exactly once
        users_in_pairs = [user for pair in called_pairs for user in pair]
        self.assertEqual(set(users), set(users_in_pairs))


if __name__ == '__main__':
    unittest.main()

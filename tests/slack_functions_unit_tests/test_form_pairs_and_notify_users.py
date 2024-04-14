import unittest
from unittest.mock import patch, MagicMock

from slack_functions import form_pairs_and_notify_users


class TestFormPairsAndNotifyUsers(unittest.TestCase):
    @patch('slack_functions.notify_user_about_pairing_issue')
    @patch('slack_functions.notify_users')
    @patch('slack_functions.group_users_by_emoji')
    def test_single_user_reaction(self, mock_group_users_by_emoji, mock_notify_users,
                                  mock_notify_user_about_pairing_issue):
        # Mock to return only one user
        mock_group_users_by_emoji.return_value = {':smile:': ['user1']}

        # Execute the function
        leftovers = form_pairs_and_notify_users({})

        # Assertions
        mock_notify_user_about_pairing_issue.assert_called_once_with('user1')
        mock_notify_users.assert_not_called()
        self.assertEqual(leftovers, [])

    @patch('slack_functions.notify_users')
    @patch('slack_functions.group_users_by_emoji')
    def test_perfect_pairing(self, mock_group_users_by_emoji, mock_notify_users):
        # Mock to return an even number of users split between emokis
        mock_group_users_by_emoji.return_value = {':smile:': ['user1', 'user2'], ':thumbsup:': ['user3', 'user4']}

        # Execute the function
        leftovers = form_pairs_and_notify_users({})

        # Assertions
        self.assertEqual(len(leftovers), 0)
        mock_notify_users.assert_called_once()

    @patch('slack_functions.notify_users')
    @patch('slack_functions.group_users_by_emoji')
    def test_two_leftover_users(self, mock_group_users_by_emoji, mock_notify_users):
        # Mock to return an even number of total users, but odd in an emoji group
        mock_group_users_by_emoji.return_value = {':smile:': ['user1', 'user2', 'user3'], ':thumbsup:': ['user5']}

        # Execute the function
        leftovers = form_pairs_and_notify_users({})

        # Assertions
        self.assertEqual(len(leftovers), 2)
        self.assertIn('user5', leftovers)
        mock_notify_users.assert_called_once()

    @patch('slack_functions.notify_users')
    @patch('slack_functions.group_users_by_emoji')
    def test_four_leftover_users(self, mock_group_users_by_emoji, mock_notify_users):
        # Mock to return an odd number of users
        mock_group_users_by_emoji.return_value = {':smile:': ['user1', 'user2', 'user3'], ':wave:': ['user4'],
                                                  ':hi:': ['user5'], ':yellow:': ['user6']}

        # Execute the function
        leftovers = form_pairs_and_notify_users({})

        # Assertions
        self.assertEqual(len(leftovers), 4)
        self.assertTrue({'user4', 'user5', 'user6'}.issubset(set(leftovers)))
        mock_notify_users.assert_called_once()

    @patch('slack_functions.notify_users')
    @patch('slack_functions.group_users_by_emoji')
    def test_trio_formation(self, mock_group_users_by_emoji, mock_notify_users):
        # Mock to return a setup that would lead to a trio
        mock_group_users_by_emoji.return_value = {':smile:': ['user1', 'user2', 'user3', 'user4'],
                                                  ':thumbsup:': ['user5']}

        # Execute the function
        leftovers = form_pairs_and_notify_users({})

        # Assertions
        self.assertEqual(len(leftovers), 0)  # Assuming trio is formed and no leftovers
        mock_notify_users.assert_called_once()

    @patch('slack_functions.notify_users')
    @patch('slack_functions.group_users_by_emoji')
    def test_no_users_at_all(self, mock_group_users_by_emoji, mock_notify_users):
        # Mock to return no users
        mock_group_users_by_emoji.return_value = {}

        # Execute the function
        leftovers = form_pairs_and_notify_users({})

        # Assertions
        self.assertEqual(len(leftovers), 0)
        mock_notify_users.assert_not_called()

    @patch('slack_functions.notify_users')
    @patch('slack_functions.group_users_by_emoji')
    def test_all_single_user_groups(self, mock_group_users_by_emoji, mock_notify_users):
        # Mock to return single-user groups
        mock_group_users_by_emoji.return_value = {':smile:': ['user1'], ':thumbsup:': ['user2'], ':wave:': ['user3']}

        # Execute the function
        leftovers = form_pairs_and_notify_users({})

        # Assertions
        self.assertEqual(len(leftovers), 3)
        mock_notify_users.assert_not_called()  # No pairs can be formed


if __name__ == '__main__':
    unittest.main()

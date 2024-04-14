import unittest

from slack_functions import group_users_by_emoji


class TestGroupUsersByEmoji(unittest.TestCase):
    def test_group_users_correctly(self):
        reactions = {
            'user1': ':smile:',
            'user2': ':smile:',
            'user3': ':thumbsup:',
            'user4': ':sad:'
        }
        expected_groups = {
            ':smile:': ['user1', 'user2'],
            ':thumbsup:': ['user3'],
            ':sad:': ['user4']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_empty_input(self):
        reactions = {}
        expected_groups = {}
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_large_reaction_set(self):
        # Generating a large number of reactions
        reactions = {f'user{i}': f':emoji{i % 5}:' for i in range(1000)}
        grouped_users = group_users_by_emoji(reactions)

        # Checking if the grouping is correct
        expected_groups = {f':emoji{i % 5}:': [] for i in range(5)}
        for i in range(1000):
            expected_groups[f':emoji{i % 5}:'].append(f'user{i}')

        self.assertEqual(grouped_users, expected_groups)

    def test_no_duplicate_users(self):
        reactions = {
            'user1': ':smile:',
            'user2': ':thumbsup:',
            'user3': ':sad:'
        }
        expected_groups = {
            ':smile:': ['user1'],
            ':thumbsup:': ['user2'],
            ':sad:': ['user3']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)


if __name__ == '__main__':
    unittest.main()

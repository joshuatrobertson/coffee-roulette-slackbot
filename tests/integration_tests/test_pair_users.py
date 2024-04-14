import unittest
from unittest.mock import patch
from slack_functions import pair_users


class TestPairUsers(unittest.TestCase):

    def setUp(self):
        self.mock_read_reactions = patch('slack_functions.read_reactions').start()
        self.mock_notify_users = patch('slack_functions.notify_users').start()
        self.mock_clear_reaction_logs = patch('slack_functions.clear_reaction_logs').start()
        self.mock_clear_timestamp_of_last_post = patch('slack_functions.clear_timestamp_of_last_post').start()

    def tearDown(self):
        # Stop all patches
        patch.stopall()

    def test_complex_reaction_patterns(self):
        self.mock_read_reactions.return_value = {
            'user1': ':coffee:',
            'user2': ':tea:',
            'user3': ':coffee:',
            'user4': ':book:',
            'user5': ':tea:',
            'user6': ':book:'
        }
        pair_users()
        args, _ = self.mock_notify_users.call_args
        notified_pairs = args[0]
        expected_pairs_set = {frozenset(['user1', 'user3']), frozenset(['user2', 'user5']),
                              frozenset(['user4', 'user6'])}
        notified_pairs_set = {frozenset(pair) for pair in notified_pairs}
        self.assertEqual(notified_pairs_set, expected_pairs_set)

    def test_multiple_reactions_from_same_user(self):
        # Simulating a user reacting with multiple emojis before pairing.
        self.mock_read_reactions.return_value = {
            'user1': ':coffee:',  # User1 reacts with coffee and then changes to tea
            'user2': ':tea:',
            'user3': ':coffee:',
            'user4': ':book:'
        }
        pair_users()
        args, _ = self.mock_notify_users.call_args
        notified_pairs = args[0]

        # Assuming that the system should take the last reaction for pairing if the function is designed this way
        # or handle it according to specific business logic.
        # In this case, we assume the function should only take the last reaction into account
        expected_pairs_set = {
            frozenset(['user1', 'user2'])}  # Assuming 'user1' is paired based on the last reaction ':tea:'
        notified_pairs_set = {frozenset(pair) for pair in notified_pairs}

        self.assertEqual(notified_pairs_set, expected_pairs_set)

    def test_no_reactions(self):
        # Test error handling when no reactions are recorded
        self.mock_read_reactions.return_value = {}
        with self.assertRaises(ValueError) as context:
            pair_users()
        self.assertEqual(str(context.exception), "Cannot pair users because fewer than two users reacted")

    def test_single_reaction(self):
        self.mock_read_reactions.return_value = {'user1': ':coffee:'}
        with self.assertRaises(ValueError):
            pair_users()

    def test_odd_number_of_users(self):
        self.mock_read_reactions.return_value = {
            'user1': ':coffee:',
            'user2': ':coffee:',
            'user3': ':coffee:'
        }
        pair_users()
        args, _ = self.mock_notify_users.call_args
        notified_pairs = args[0]
        self.assertEqual(len(notified_pairs), 1)
        self.assertIn('user3', sum(notified_pairs, ()))

    def test_all_same_emoji(self):
        self.mock_read_reactions.return_value = {
            'user1': ':coffee:',
            'user2': ':coffee:',
            'user3': ':coffee:',
            'user4': ':coffee:',
            'user5': ':coffee:',
            'user6': ':coffee:'
        }
        pair_users()
        args, _ = self.mock_notify_users.call_args
        notified_pairs = args[0]
        self.assertEqual(len(notified_pairs), 3)

    def test_repeated_reactions_from_same_user(self):
        # Assuming the function picks the last reaction only, and simulating a user changing their reaction.
        # Initially both users react with different emojis
        self.mock_read_reactions.return_value = {
            'user1': ':coffee:',
            'user2': ':tea:',
        }
        # Assume 'user1' reacts again, changing their choice
        self.mock_read_reactions.return_value.update({'user1': ':tea:'})
        pair_users()
        args, _ = self.mock_notify_users.call_args
        notified_pairs = args[0]
        # Check that the pair includes the updated reaction from 'user1'
        self.assertIn(('user1', 'user2'), {tuple(sorted(pair)) for pair in notified_pairs})

    def test_mixed_reactions_from_users(self):
        self.mock_read_reactions.return_value = {
            'user1': ':coffee:',
            'user2': ':coffee:',
            'user3': ':tea:',
            'user4': ':milk:',
            'user5': ':tea:',
            'user6': ':water:',
        }
        pair_users()
        args, _ = self.mock_notify_users.call_args
        notified_pairs = args[0]
        # Expecting two pairs from coffee and tea, with 'user4' and 'user6' left unpaired
        expected_pairs_set = {frozenset(['user1', 'user2']), frozenset(['user3', 'user5'])}
        notified_pairs_set = {frozenset(pair) for pair in notified_pairs}

        self.assertEqual(notified_pairs_set, expected_pairs_set)

    def test_unique_reactions_each_user(self):
        self.mock_read_reactions.return_value = {
            'user1': ':coffee:',
            'user2': ':tea:',
            'user3': ':water:',
            'user4': ':juice:',
        }
        pair_users()
        args, _ = self.mock_notify_users.call_args
        notified_pairs = args[0]
        # Expecting 2 pairs that are assigned randomly
        self.assertEqual(len(notified_pairs), 2)

    def test_simultaneous_emoji_changes(self):
        # Initial reactions set
        initial_reactions = {
            'user1': ':coffee:',
            'user2': ':tea:',
            'user3': ':coffee:',
        }
        self.mock_read_reactions.return_value = initial_reactions
        pair_users()  # first call to pair users with initial reactions

        # Updated reactions set
        updated_reactions = {
            'user1': ':tea:',
            'user2': ':coffee:',
            'user3': ':water:',
        }
        self.mock_read_reactions.return_value = updated_reactions
        pair_users()  # second call to pair users with updated reactions
        args, _ = self.mock_notify_users.call_args
        notified_pairs = args[0]

        # Check that pairs reflect updated reactions, expecting 1 triple
        self.assertEqual(len(notified_pairs), 1)

    def test_error_handling_in_reaction_reading(self):
        self.mock_read_reactions.side_effect = Exception("File error")
        with self.assertRaises(Exception):
            pair_users()

    def test_large_group_handling(self):
        # created reactions for 50 'tea' and 50 'coffee' emojis
        reactions = {'user{}'.format(i): ':coffee:' if i % 2 == 0 else ':tea:' for i in range(100)}
        self.mock_read_reactions.return_value = reactions
        pair_users()
        args, _ = self.mock_notify_users.call_args
        notified_pairs = args[0]
        # As is is an even number, there should be 50 pairs
        self.assertEqual(len(notified_pairs), 50)

    def test_handling_of_identical_reactions(self):
        self.mock_read_reactions.return_value = {
            'user1': ':coffee:',
            'user2': ':coffee:',
            'user3': ':coffee:',
            'user4': ':coffee:'
        }
        pair_users()
        args, _ = self.mock_notify_users.call_args
        notified_pairs = args[0]
        self.assertEqual(len(notified_pairs), 2)

    if __name__ == '__main__':
        unittest.main()

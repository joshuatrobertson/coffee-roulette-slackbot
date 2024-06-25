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

    def test_group_users_with_variations(self):
        reactions = {
            'user1': ':thumbsup:',
            'user2': ':thumbsup::skin-tone-2:',
            'user3': ':thumbsup::skin-tone-3:',
            'user4': ':smile:',
            'user5': ':smile::skin-tone-1:'
        }
        expected_groups = {
            ':thumbsup:': ['user1', 'user2', 'user3'],
            ':smile:': ['user4', 'user5']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_group_users_with_complex_names(self):
        reactions = {
            'user1': ':woman-walking:',
            'user2': ':woman-walking::skin-tone-4:',
            'user3': ':woman-walking::skin-tone-5:',
            'user4': ':man-running:',
            'user5': ':man-running::skin-tone-2:'
        }
        expected_groups = {
            ':woman-walking:': ['user1', 'user2', 'user3'],
            ':man-running:': ['user4', 'user5']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_group_users_with_numbers(self):
        reactions = {
            'user1': ':one:',
            'user2': ':one:',
            'user3': ':two:',
            'user4': ':three:',
            'user5': ':three::skin-tone-3:'
        }
        expected_groups = {
            ':one:': ['user1', 'user2'],
            ':two:': ['user3'],
            ':three:': ['user4', 'user5']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_group_users_with_flags(self):
        reactions = {
            'user1': ':flag-us:',
            'user2': ':flag-us:',
            'user3': ':flag-gb:',
            'user4': ':flag-fr:',
            'user5': ':flag-de:'
        }
        expected_groups = {
            ':flag-us:': ['user1', 'user2'],
            ':flag-gb:': ['user3'],
            ':flag-fr:': ['user4'],
            ':flag-de:': ['user5']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_group_users_with_mixed_emoji_variations(self):
        reactions = {
            'user1': ':man-gesturing-ok:',
            'user2': ':man-gesturing-ok::skin-tone-2:',
            'user3': ':man-gesturing-ok::skin-tone-3:',
            'user4': ':woman-gesturing-ok:',
            'user5': ':woman-gesturing-ok::skin-tone-1:'
        }
        expected_groups = {
            ':man-gesturing-ok:': ['user1', 'user2', 'user3'],
            ':woman-gesturing-ok:': ['user4', 'user5']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_group_users_with_face_emojis(self):
        reactions = {
            'user1': ':grinning:',
            'user2': ':grinning:',
            'user3': ':smiley:',
            'user4': ':smiley::skin-tone-2:',
            'user5': ':laughing:'
        }
        expected_groups = {
            ':grinning:': ['user1', 'user2'],
            ':smiley:': ['user3', 'user4'],
            ':laughing:': ['user5']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_group_users_with_hand_emojis(self):
        reactions = {
            'user1': ':waving_hand:',
            'user2': ':waving_hand::skin-tone-1:',
            'user3': ':clapping_hands:',
            'user4': ':clapping_hands::skin-tone-2:',
            'user5': ':thumbs_up:'
        }
        expected_groups = {
            ':waving_hand:': ['user1', 'user2'],
            ':clapping_hands:': ['user3', 'user4'],
            ':thumbs_up:': ['user5']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_group_users_with_animal_emojis(self):
        reactions = {
            'user1': ':dog:',
            'user2': ':dog:',
            'user3': ':cat:',
            'user4': ':mouse:',
            'user5': ':rabbit:'
        }
        expected_groups = {
            ':dog:': ['user1', 'user2'],
            ':cat:': ['user3'],
            ':mouse:': ['user4'],
            ':rabbit:': ['user5']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_group_users_with_food_emojis(self):
        reactions = {
            'user1': ':apple:',
            'user2': ':apple:',
            'user3': ':banana:',
            'user4': ':strawberry:',
            'user5': ':grapes:'
        }
        expected_groups = {
            ':apple:': ['user1', 'user2'],
            ':banana:': ['user3'],
            ':strawberry:': ['user4'],
            ':grapes:': ['user5']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)

    def test_group_users_with_transport_emojis(self):
        reactions = {
            'user1': ':car:',
            'user2': ':car:',
            'user3': ':bus:',
            'user4': ':bicycle:',
            'user5': ':airplane:'
        }
        expected_groups = {
            ':car:': ['user1', 'user2'],
            ':bus:': ['user3'],
            ':bicycle:': ['user4'],
            ':airplane:': ['user5']
        }
        grouped_users = group_users_by_emoji(reactions)
        self.assertEqual(grouped_users, expected_groups)


if __name__ == '__main__':
    unittest.main()

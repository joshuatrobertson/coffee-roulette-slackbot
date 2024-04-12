import unittest
from slack_functions import extract_emojis_from_message


class TestExtractEmojis(unittest.TestCase):

    def test_extract_with_colon(self):
        message = "Hello there!\n1: :smile:\n2: :coffee:\n3: :robot_face:"
        expected_emojis = ['smile', 'coffee', 'robot_face']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_extract_with_dot(self):
        message = "Test!\n1. :laughing:\n2. :sun_with_face:\n3. :moon:"
        expected_emojis = ['laughing', 'sun_with_face', 'moon']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_no_emojis(self):
        message = "No emojis here!\nJust text.\nAnother line."
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_mixed_formats(self):
        message = "Mixed formats here!\n1: :star:\n2. :heart:\n3: :earth_americas:"
        expected_emojis = ['star', 'heart', 'earth_americas']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)


if __name__ == '__main__':
    unittest.main()

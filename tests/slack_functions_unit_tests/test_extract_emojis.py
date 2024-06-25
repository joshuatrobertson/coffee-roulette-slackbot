import unittest

import self

from slack_functions import extract_emojis_from_message


class TestExtractEmojis(unittest.TestCase):
    def test_extract_with_colon(self):
        message = "Hello there!\n1: :smile:\n2: :coffee:\n3: :robot_face:"
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_extract_with_dot(self):
        message = "Test!\n1. :laughing:\n2. :sun_with_face:\n3. :moon:"
        expected_emojis = ['laughing', 'sun_with_face', 'moon']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_extract_in_middle_of_text(self):
        message = "Test!\n1. :laughing: this is the end of a line\n2. :sun_with_face:\n3. :moon: eol"
        expected_emojis = ['sun_with_face']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_no_emojis(self):
        message = "No emojis here!\nJust text.\nAnother line."
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_mixed_formats(self):
        message = "Mixed formats here!\n1: :star:\n2. line text :heart:\n3: :earth_americas:"
        expected_emojis = ['heart']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_empty_lines(self):
        message = "Empty lines\n1. \n2. \n3. "
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_multiple_emojis_in_line(self):
        message = "Multiple emojis\n1. :smile: :laughing:\n2. :coffee:\n3. :robot_face: :sun_with_face:"
        expected_emojis = ['coffee']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_whitespace_handling(self):
        message = "Whitespace handling\n1.    :smile:    \n2.  :coffee:   \n3. :robot_face: "
        expected_emojis = ['smile', 'coffee', 'robot_face']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_no_emoji_after_dot(self):
        message = "No emoji after dot\n1. Test line\n2. Another line\n3. Last line"
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_special_characters(self):
        message = "Special characters\n1. :smile:!@#\n2. $%^:coffee:&*()\n3. :robot_face:<>?/"
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_line_breaks_in_text(self):
        message = "Line breaks\n1.\n:laughing:\n2. \n:sun_with_face:\n3.\n:moon:"
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_single_digit_beyond_three(self):
        message = "Single digit beyond three\n4. :smile:\n5. :coffee:"
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_missing_number_before_dot(self):
        message = "Missing number before dot\n. :smile:\n. :coffee:"
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_zero_and_negative_numbers(self):
        message = "Zero and negative numbers\n0. :smile:\n-1. :coffee:"
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_non_sequential_numbers(self):
        message = "Non-sequential numbers\n4. :smile:\n5. :coffee:"
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_long_text_with_emoji_at_end(self):
        message = "Long text with emoji at end\n1. This is a long line of text that ends with an emoji :smile:"
        expected_emojis = ['smile']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_single_digit_lines_with_text_and_special_characters(self):
        message = "Single digit lines with text and special characters\n1. Hello! :smile:\n2. Welcome :) :coffee:\n3. Hi there :robot_face:"
        expected_emojis = ['smile', 'coffee', 'robot_face']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_lines_with_only_emojis_and_no_text(self):
        message = "Only emojis\n1. :smile:\n2. :coffee:\n3. :robot_face:"
        expected_emojis = ['smile', 'coffee', 'robot_face']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_lines_with_leading_or_trailing_whitespace(self):
        message = "Leading or trailing whitespace\n  1. :smile:   \n\t2. :coffee: \n 3. :robot_face:  "
        expected_emojis = ['smile', 'coffee', 'robot_face']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_multiline_text_without_numbering(self):
        message = "Multiline text without numbering\nThis is a test\n:smile: should not be extracted\n:coffee: should not be extracted"
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_mixed_correct_and_incorrect_formats(self):
        message = "Mixed formats\n1. :smile:\nIncorrect format\n3. :robot_face: eol\n2. :coffee:"
        expected_emojis = ['smile', 'coffee']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_text_with_numbers_but_no_dots(self):
        message = "Numbers but no dots\n1 :smile:\n2 :coffee:\n3 :robot_face:"
        expected_emojis = []
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

    def test_lines_with_invalid_characters_before_emoji(self):
        message = "Invalid characters before emoji\n1. text :smile:\n2. :coffee: text\n3. #!@ :robot_face:"
        expected_emojis = ['smile', 'robot_face']
        self.assertEqual(extract_emojis_from_message(message), expected_emojis)

if __name__ == '__main__':
    unittest.main()

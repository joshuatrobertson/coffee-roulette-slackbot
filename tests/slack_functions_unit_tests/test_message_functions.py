import unittest
from unittest.mock import patch, MagicMock, call
import logging
from slack_functions import message_pair, message_trio, slack_app


class TestMessageFunctions(unittest.TestCase):

    @patch('your_module.slack_app.client.chat_postMessage')
    def test_message_pair_success(self, mock_chat_post):
        # Setup
        mock_chat_post.return_value = {'ok': True}

        # Action
        message_pair('U123', 'U456')

        # Assert
        self.assertEqual(mock_chat_post.call_count, 2)
        calls = [(({'channel': 'U123',
                    'text': 'You\'ve been paired with <@U456> for #coffee-roulette! Please arrange a meeting.'},),),
                 (({'channel': 'U456',
                    'text': 'You\'ve been paired with <@U123> for #coffee-roulette! Please arrange a meeting.'},),)]
        mock_chat_post.assert_has_calls(calls, any_order=True)

    @patch('your_module.slack_app.client.chat_postMessage')
    @patch('your_module.logging.error')
    def test_message_pair_failure(self, mock_logging, mock_chat_post):
        # Setup
        mock_chat_post.side_effect = [{'ok': False, 'error': 'some_error'}, {'ok': True}]

        # Action
        message_pair('U123', 'U456')

        # Assert
        mock_logging.assert_called_once_with('Failed to send message to U123: some_error')

    @patch('your_module.slack_app.client.chat_postMessage')
    def test_message_trio_success(self, mock_chat_post):
        # Setup
        mock_chat_post.return_value = {'ok': True}

        # Action
        message_trio('U123', 'U456', 'U789')

        # Assert
        self.assertEqual(mock_chat_post.call_count, 3)
        expected_calls = [
            (({'channel': 'U123',
               'text': 'You\'re in a trio with <@U456> and <@U789> for #coffee-roulette! Please arrange a meeting.'},),),
            (({'channel': 'U456',
               'text': 'You\'re in a trio with <@U123> and <@U789> for #coffee-roulette! Please arrange a meeting.'},),),
            (({'channel': 'U789',
               'text': 'You\'re in a trio with <@U123> and <@U456> for #coffee-roulette! Please arrange a meeting.'},),)
        ]
        mock_chat_post.assert_has_calls(expected_calls, any_order=True)

    @patch('your_module.slack_app.client.chat_postMessage')
    @patch('your_module.logging.error')
    def test_message_trio_failure(self, mock_logging, mock_chat_post):
        # Setup
        mock_chat_post.side_effect = [{'ok': False, 'error': 'error1'}, {'ok': False, 'error': 'error2'},
                                      {'ok': False, 'error': 'error3'}]

        # Action
        message_trio('U123', 'U456', 'U789')

        # Assert
        expected_logs = [call('Failed to send message to U123: error1'),
                         call('Failed to send message to U456: error2'),
                         call('Failed to send message to U789: error3')]
        mock_logging.assert_has_calls(expected_logs, any_order=True)


if __name__ == '__main__':
    unittest.main()

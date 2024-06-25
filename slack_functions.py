import logging
import os
import random
import datetime
import emoji
import emoji_data_python
from dotenv import load_dotenv
from slack_bolt import App
import re

from slack_sdk.errors import SlackApiError

from ai_functions import generate_weekly_message

bot_added_emojis = []

# Load environment variables from .env file
load_dotenv()

# Initialize Slack Bolt app
slack_app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

# Assuming a simple structure to store user responses
user_responses = {}


# Create a dictionary to map Unicode emojis to Slack-compatible names
def build_emoji_slack_map():
    emoji_slack_map = {}
    for emoji in emoji_data_python.emoji_data:
        # Slack uses some custom names, this maps known Unicode names to Slack's equivalent.
        # You might need to manually adjust mappings for perfect compatibility.
        slack_name = emoji.short_name.replace("-", "_")
        emoji_slack_map[emoji.char] = slack_name
    return emoji_slack_map


emoji_slack_map = build_emoji_slack_map()


# Function to generate the weekly message
def generate_message_for_week():
    message_content = generate_weekly_message()
    return message_content


def get_slack_emoji_name(unicode_emoji):
    emoji_slack_map = {e.char: e.short_name.replace("-", "_") for e in emoji_data_python.emoji_data}
    return emoji_slack_map.get(unicode_emoji, "")


# Function to post the weekly message
def post_weekly_message(retry_count=0, max_retries=10):
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    starting_line = f":nyan-josh-coffee: :coffee_parrot_1: <!channel> :coffee_parrot_1: :nyan-josh-coffee:"
    if retry_count >= max_retries:
        logging.error(f"Failed to post message after {max_retries} attempts. Emoji addition failed.")
        return
    ai_message = generate_message_for_week()
    message_content = starting_line + "\n" + ai_message

    # Try to fetch the emojis
    emojis = extract_emojis_from_message(message_content)
    if len(emojis) != 3:
        logging.error(f"Error: Number of extracted emojis is not 3 and is {emojis}. Retrying...")
        post_weekly_message(retry_count + 1, max_retries)

        return

    # Append the note only after confirming emoji count
    message_content += ("\n\n\n-------+-------\n\n\n_This message was generated and posted by the CoffeeRouletteBot "
                        ":robot_face: using Watsonx generative AI APIs. For any "
                        "issues, bugs or suggestions, please contact <@U02GDNQPE04|josh>_ :josh-nyan-coffee:\n_Known bugs: none_ "
                        ":slightly_smiling_face:")
    logging.debug(f"SLACK_CHANNEL_ID: {os.getenv('SLACK_CHANNEL_ID')}")


    message_ts = slack_app.client.chat_postMessage(channel=channel_id, text=message_content)['ts']

    for emoji in emojis:
        try:
            slack_app.client.reactions_add(channel=channel_id, name=emoji, timestamp=message_ts)
        except Exception as e:
            slack_app.client.chat_delete(channel=channel_id, ts=message_ts)
            post_weekly_message(retry_count + 1, max_retries)  # Optionally retry if we don't have 3 emojis
            return


# Function to fetch reactions from Slack
def fetch_reactions_from_slack(message_ts):
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    bot_user_id = os.getenv('SLACK_BOT_USER_ID')
    try:
        response = slack_app.client.reactions_get(channel=channel_id, timestamp=message_ts)
        reactions = response.get('message', {}).get('reactions', [])
        reactions_dict = {}
        for reaction in reactions:
            for user in reaction['users']:
                if user != bot_user_id:  # Ensure bot is not included
                    reactions_dict[user] = reaction['name']
        return reactions_dict
    except SlackApiError as e:
        logging.error(f"Error fetching reactions: {e.response['error']}")
        return {}


# Extract emojis where the line starts with a number between 1 and 3
def extract_emojis_from_message(message_content):
    logging.debug("Extracting emojis..")
    emojis_in_message = []
    try:
        for line in message_content.split('\n'):
            match = re.match(r'^[1-3]\.\s.*(:[a-zA-Z0-9_]+:)\s*$', line.strip())  # Check for lines starting with 1., 2., or 3. followed by space and ending with emoji
            if match:
                # Find all emoji matches in the line
                emoji_matches = re.findall(r':[a-zA-Z0-9_]+:', line)
                if len(emoji_matches) == 1:  # Ensure only one emoji is present
                    emoji_name = emoji_matches[0].strip(':')
                    logging.debug(f"Found emoji: {emoji_name}")
                    emojis_in_message.append(emoji_name)
        return emojis_in_message
    except Exception as e:
        logging.error(f"Failed to extract emojis due to: {str(e)}")
        return []
def group_users_by_emoji(reactions):
    grouped_users = {}
    for user, emoji in reactions.items():
        grouped_users.setdefault(emoji, []).append(user)
    logging.info(f"Users grouped by emoji: {grouped_users}")
    return grouped_users


def handle_leftovers(leftover_users):
    random.shuffle(leftover_users)
    pairs = []

    # Check if there are exactly three users left, handle trio case first
    if len(leftover_users) == 3:
        trio = (leftover_users.pop(), leftover_users.pop(), leftover_users.pop())
        notify_users([trio])
        return  # Exit the function since no more users to pair

    # Continue with normal pair formation for other cases
    while len(leftover_users) > 1:
        pair = (leftover_users.pop(), leftover_users.pop())
        pairs.append(pair)

    # Notify all formed pairs
    notify_users(pairs)


def pair_users():
    # Get timestamp of the last bot post
    current_ts = get_last_message_ts()
    if current_ts:
        # Post a message indicating pairing is happening
        channel_id = os.getenv("SLACK_CHANNEL_ID")
        try:
            slack_app.client.chat_postMessage(
                channel=channel_id,
                text="Pairing users now! Look out for a message from the bot and arrange a call! :telephone-calling-blue: :coffee:",
                thread_ts=current_ts  # Post this message as a reply to the original post
            )
        except SlackApiError as e:
            logging.error(f"Error posting pairing announcement: {e.response['error']}")

        reactions = fetch_reactions_from_slack(current_ts)
        # Group users by emoji and form pairs
        leftover_users = form_pairs_and_notify_users(reactions)
        # Randomly assign any leftovers
        handle_leftovers(leftover_users)


def form_pairs_and_notify_users(reactions):
    grouped_users = group_users_by_emoji(reactions)
    total_users = sum(len(users) for users in grouped_users.values())
    pairs = []
    leftover_users = []

    # Early exit if no users are available
    if total_users == 0:
        return []

    # Check if there is exactly one user overall and handle it
    if total_users == 1:
        single_user = next(iter(next(iter(grouped_users.values()))))
        notify_user_about_pairing_issue(single_user)
        return []  # Return nothing as a leftover (no pairs or trios can be formed)

    # Form pairs
    for emoji, users in grouped_users.items():
        random.shuffle(users)
        while len(users) >= 2:
            pair = (users.pop(), users.pop())
            pairs.append(pair)
        leftover_users.extend(users)

    # If there is an odd number, add the last user to a trio, that way leftover_users can all be paired and should only
    # have 1 trio
    if len(leftover_users) % 2 == 1 and pairs:
        pairs[-1] += (leftover_users.pop(),)

    # Notify all formed pairs if any pairs exist
    if pairs:
        notify_users(pairs)

    # Return an even number of leftover_users
    return leftover_users


def notify_users(pairs):
    for pair in pairs:
        if len(pair) == 2:
            logging.info(f"Message sent to pair: {pair[0], pair[1]}")
            message_pair(pair[0], pair[1])
        elif len(pair) == 3:
            logging.info(f"Message sent to trio: {pair[0], pair[1], pair[2]}")
            message_trio(pair[0], pair[1], pair[2])


def get_last_message_ts():
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    user_id = os.getenv("SLACK_BOT_USER_ID")
    try:
        # Fetch messages from the channel
        response = slack_app.client.conversations_history(channel=channel_id, limit=100)
        messages = response.get('messages', [])

        # Find the last message by the user
        for message in messages:
            if message.get('user') == user_id:
                return message.get('ts')
    except SlackApiError as e:
        logging.error(f"Error fetching conversations: {e.response['error']}")
    return None


def delete_last_post():
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    ts = get_last_message_ts()
    try:
        # Delete the message
        response = slack_app.client.chat_delete(channel=channel_id, ts=ts)
        logging.info(f"Deleted message: {response['ok']}")
    except SlackApiError as e:
        logging.error(f"Error deleting message with id {channel_id} and TS {ts}: {e.response['error']}")


def notify_user_about_pairing_issue(user):
    slack_app.client.chat_postMessage(channel=user,
                                      text=f"Hi, <@{user}>, you were the only one who reacted to coffee roulette "
                                           f"this week :upside-down-face:, please try again next week")


def message_pair(user1, user2):
    print(f"Sending message to pair: {user1}, {user2}")
    response_1 = slack_app.client.chat_postMessage(channel=user1,
                                                   text=f"Hi, <@{user1}>, you've been paired with <@{user2}> for "
                                                        f"#coffee-roulette! Please arrange a meeting.")
    response_2 = slack_app.client.chat_postMessage(channel=user2,
                                                   text=f"Hi, <@{user2}>, you've been paired with <@{user1}> for "
                                                        f"#coffee-roulette! Please arrange a meeting.")

    if not response_1['ok']:
        logging.error(f"Failed to send message to {user1}: {response_1['error']}")
    if not response_2['ok']:
        logging.error(f"Failed to send message to {user2}: {response_2['error']}")


def message_trio(user1, user2, user3):
    print(f"Sending message to trio: {user1}, {user2}, {user3}")
    response_1 = slack_app.client.chat_postMessage(channel=user1,
                                                   text=f"Hi, <@{user1}>, you're in a trio with <@{user2}> and <@{user3}> for #coffee-roulette! Please arrange a meeting.")
    response_2 = slack_app.client.chat_postMessage(channel=user2,
                                                   text=f"Hi, <@{user2}>, you're in a trio with <@{user1}> and <@{user3}> for #coffee-roulette! Please arrange a meeting.")
    response_3 = slack_app.client.chat_postMessage(channel=user3,
                                                   text=f"Hi, <@{user3}>, you're in a trio with <@{user1}> and <@{user2}> for #coffee-roulette! Please arrange a meeting.")

    if not response_1['ok']:
        logging.error(f"Failed to send message to {user1}: {response_1['error']}")
    if not response_2['ok']:
        logging.error(f"Failed to send message to {user2}: {response_2['error']}")
    if not response_3['ok']:
        logging.error(f"Failed to send message to {user2}: {response_2['error']}")

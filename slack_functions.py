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
from file_operations import log_reaction, read_reactions, clear_reaction_logs, store_message_ts, \
    get_current_weekly_message_ts

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
    print("Message content in generate_weekly_message: " + message_content)
    return message_content


def get_slack_emoji_name(unicode_emoji):
    # Retrieve the Slack-compatible name from the map
    return emoji_slack_map.get(unicode_emoji, "")


# Function to post the weekly message
def post_weekly_message(retry_count=0, max_retries=3):
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    starting_line = f"Morning <!{channel_id}>, it's Monday which means time for #coffee-roulette!'"
    if retry_count >= max_retries:
        print(f"Failed to post message after {max_retries} attempts. Emoji addition failed.")
        return
    ai_message = generate_message_for_week()
    message_content = starting_line + "\n" + ai_message

    # Try to fetch the emojis
    emojis = extract_emojis_from_message(message_content)
    if len(emojis) != 3:
        print("Error: Number of extracted emojis is not 3. Retrying...")
        post_weekly_message(retry_count + 1, max_retries)
        return

    # Append the note only after confirming emoji count
    message_content += ("\n\n\n-------+-------\n\n\n_This message was generated and posted by the CoffeeRouletteBot "
                        ":robot_face: using generative AI and therefore sometimes my output may be...interesting. For any "
                        "issues or bugs, please contact <@U06T3N4P2M8|josh>_ :josh-nyan-coffee:\n_Known bugs: none_ :smile:")

    message_ts = slack_app.client.chat_postMessage(channel=channel_id, text=message_content)['ts']
    store_message_ts(message_ts)

    for emoji in emojis:
        try:
            print("Adding Emoji", emoji)
            slack_app.client.reactions_add(channel=channel_id, name=emoji, timestamp=message_ts)
        except Exception as e:
            print(f"Error adding reaction {emoji}: {e}")
            slack_app.client.chat_delete(channel=channel_id, ts=message_ts)
            print("Deleted message due to emoji addition failure.")
            post_weekly_message(retry_count + 1, max_retries)  # Optionally retry if we don't have 3 emojis
            return


# use a regex to match both "1. :emoji:" and "1: :emoji:"
# TODO: Can remove if the below works, as better to input with actual emojis
def extract_emojis_from_message_slack_format(message_content):
    emoji_pattern = r'^\d[.:].*:(\w+):'
    emojis_list = re.findall(emoji_pattern, message_content, flags=re.MULTILINE)
    return emojis_list


# Extract emojis where the line starts with a number between 1 and 3
def extract_emojis_from_message(message_content):
    print("Extracting emojis..")
    emojis_in_message = []
    try:
        for line in message_content.split('\n'):
            if re.match(r'^[1-3]\.', line.strip()):
                # Extract emojis from each line and convert them to Slack names
                slack_emojis = [get_slack_emoji_name(char) for char in line if char in emoji_slack_map]
                print(f"Found emojis: {slack_emojis}")
                emojis_in_message.extend(slack_emojis)
        return emojis_in_message
    except Exception as e:  # Broadening error handling to catch all exceptions
        logging.error(f"Failed to extract emojis due to: {str(e)}")
        return []


# handles the reaction_added event - adds all emojis, so if a user reacts in any way to the post they will be matched
@slack_app.event("reaction_added")
def handle_reaction_added(event):
    current_ts = get_current_weekly_message_ts()

    try:
        # Attempt to extract timestamp from event['item']
        reaction_msg_ts = event['event']['item']['ts']
        if reaction_msg_ts == current_ts:
            user_id = event['event']['user']
            reaction = event['event']['reaction']
            log_reaction(user_id, reaction)

    except KeyError as e:
        logging.error(f"KeyError encountered: {str(e)}")
        logging.error(f"Received event: {event}")


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
    # Read from file
    reactions = read_reactions()
    # Group users by emoji and form pairs
    leftover_users = form_pairs_and_notify_users(reactions)
    # Randomly assign any leftovers
    handle_leftovers(leftover_users)
    # Clear reactions to start the roulette again
    clear_reaction_logs()


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
    user_id = os.getenv("SLACK_BOT_USER_ID")
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
                                           f"this week :upside_down_face:, please try again next week")


def message_pair(user1, user2):
    print(f"Sending message to pair: {user1}, {user2}")
    response_1 = slack_app.client.chat_postMessage(channel=user1,
                                                   text=f"You've been paired with <@{user2}> for #coffee-roulette! Please arrange a meeting.")
    response_2 = slack_app.client.chat_postMessage(channel=user2,
                                                   text=f"You've been paired with <@{user1}> for #coffee-roulette! Please arrange a meeting.")

    if not response_1['ok']:
        logging.error(f"Failed to send message to {user1}: {response_1['error']}")
    if not response_2['ok']:
        logging.error(f"Failed to send message to {user2}: {response_2['error']}")


def message_trio(user1, user2, user3):
    print(f"Sending message to trio: {user1}, {user2}, {user3}")
    response_1 = slack_app.client.chat_postMessage(channel=user1,
                                                   text=f"You're in a trio with <@{user2}> and <@{user3}> for #coffee-roulette! Please arrange a meeting.")
    response_2 = slack_app.client.chat_postMessage(channel=user2,
                                                   text=f"You're in a trio with <@{user1}> and <@{user3}> for #coffee-roulette! Please arrange a meeting.")
    response_3 = slack_app.client.chat_postMessage(channel=user3,
                                                   text=f"You're in a trio with <@{user1}> and <@{user2}> for #coffee-roulette! Please arrange a meeting.")

    if not response_1['ok']:
        logging.error(f"Failed to send message to {user1}: {response_1['error']}")
    if not response_2['ok']:
        logging.error(f"Failed to send message to {user2}: {response_2['error']}")
    if not response_3['ok']:
        logging.error(f"Failed to send message to {user2}: {response_2['error']}")

        # test

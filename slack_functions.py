import os
import random
import datetime
from dotenv import load_dotenv
from slack_bolt import App
import re
from ai_functions import generate_weekly_message
from file_operations import log_reaction, read_reactions, clear_reaction_logs, store_message_ts, \
    get_current_weekly_message_ts
import tempfile

channel_id = "C06T4HJ4Y5Q"
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


# Function to generate the weekly message
def generate_message_for_week(use_numbered_emojis=False):
    today = datetime.date.today().strftime('%d-%m')
    # Customize this message as needed
    message_content = generate_weekly_message(today, use_numbered_emojis)
    print("Message content in generate_weekly_message: " + message_content)
    return message_content


# Function to post the weekly message
def post_weekly_message(retry_count=0, max_retries=3):
    if retry_count >= max_retries:
        print(f"Failed to post message after {max_retries} attempts. Emoji addition failed.")
        return

    use_numbered_emojis = retry_count == 2  # Use numbered emojis only on the third attempt
    message_content = generate_message_for_week(use_numbered_emojis)
    print("Generated content: " + message_content)

    # Try to fetch the emojis
    emojis = extract_emojis_from_message(message_content)
    print("Extracted Emojis:", emojis)
    if len(emojis) != 3:
        print("Error: Number of extracted emojis is not 3. Retrying...")
        post_weekly_message(retry_count + 1, max_retries)
        return

    # Append the note only after confirming emoji count
    message_content += ("\n\n\n-------+-------\n\n\n_This message was generated and posted by the CDSCoffeeRouletteBot "
                        ":robot_face: using generative AI and therefore sometimes my output may be...interesting. For any "
                        "issues or bugs, please contact <@U06T3N4P2M8|josh>_ :josh-nyan-coffee:\n_Known bugs: none_ :smile:")

    message_ts = slack_app.client.chat_postMessage(channel=channel_id, text=message_content)['ts']
    store_message_ts(message_ts)
    print("Timestamp of posted message: " + message_ts)

    for emoji in emojis:
        try:
            print("Adding Emoji", emoji)
            slack_app.client.reactions_add(channel=channel_id, name=emoji, timestamp=message_ts)
        except Exception as e:
            print(f"Error adding reaction {emoji}: {e}")
            slack_app.client.chat_delete(channel=channel_id, ts=message_ts)
            print("Deleted message due to emoji addition failure.")
            post_weekly_message(retry_count + 1, max_retries)  # Optionally retry
            return


# use a regex to match both "1. :emoji:" and "1: :emoji:"
def extract_emojis_from_message(message_content):
    emoji_pattern = r'^\d[.:].*:(\w+):'
    emojis_list = re.findall(emoji_pattern, message_content, flags=re.MULTILINE)
    return emojis_list


# handles the reaction_added event - adds all emojis, so if a user reacts in any way to the post they will be matched
@slack_app.event("reaction_added")
def handle_reaction_added(event):
    current_ts = get_current_weekly_message_ts()
    print("TIMESTAMP: " + current_ts)
    print(f"Timestamp of weekly message after fetching is {current_ts}")
    print("reaction stored!")

    try:
        # Attempt to extract timestamp from event['item']
        reaction_msg_ts = event['event']['item']['ts']
        print("Timestamp of reaction: " + reaction_msg_ts)

        if reaction_msg_ts == current_ts:
            user_id = event['event']['user']
            reaction = event['event']['reaction']
            log_reaction(user_id, reaction)

    except KeyError as e:
        # Log the exception and the event that caused it
        print(f"KeyError encountered: {str(e)}")
        print(f"Received event: {event}")


def notify_users(pairs):
    for pair in pairs:
        message_users(*pair)


def pair_users():
    reactions = read_reactions()  # Expected to return a dict like {'U123': 'emoji_one', 'U456': 'emoji_two', ...}
    grouped_users = {}  # Dict to hold users grouped by emoji

    # Group users by their reactions
    for user, emoji in reactions.items():
        emoji_tuple = tuple(emoji)  # Convert list to tuple
        if emoji_tuple not in grouped_users:
            grouped_users[emoji_tuple] = []
        grouped_users[emoji_tuple].append(user)

    # Create pairs within each emoji group
    pairs = []
    for users in grouped_users.values():
        random.shuffle(users)  # Shuffle users within the same emoji group
        while len(users) >= 2:
            pairs.append((users.pop(), users.pop()))

        # If an odd number of users, optionally add the last one to the last created pair
        if users and pairs:
            pairs[-1] += (users.pop(),)

    # Notify users of their pairs or trios
    notify_users(pairs)
    clear_reaction_logs()  # Clear the file after pairing


# Message either 2 or 3 users
def message_users(*users):
    if len(users) < 2:
        raise ValueError("At least two users are required to send a message.")

    # Generate the message for each user by mentioning all other users
    for i in range(len(users)):
        # Create a list of all users except the current one being messaged
        other_users = [f"<@{user}>" for j, user in enumerate(users) if i != j]
        if len(other_users) > 1: # other users is greater than 1 i.e. a trio
            message_text = f"You've been paired with {', '.join(other_users[:-1])} and {other_users[-1]} for #cds-coffee-roulette! Please arrange a meeting."
        else:
            message_text = f"You've been paired with {other_users[0]} for #cds-coffee-roulette! Please arrange a meeting." # pair as only one other user
        # Send the message to the current user
        slack_app.client.chat_postMessage(channel=users[i], text=message_text)

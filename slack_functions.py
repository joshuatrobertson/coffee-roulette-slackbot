import os
import random
import datetime
from dotenv import load_dotenv
from slack_bolt import App
import re
from ai_functions import generate_weekly_message
from file_operations import log_reaction, read_reactions, clear_reaction_logs, store_message_ts, get_current_weekly_message_ts
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
    current_ts = get_current_weekly_message_ts()  # Get the timestamp of the current weekly message
    print("reaction stored!")
    reaction_msg_ts = event['item']['ts']
    if reaction_msg_ts == current_ts:
        user_id = event['user']
        reaction = event['reaction']
        log_reaction(user_id, reaction)


def notify_users(pairs):
    for pair in pairs:
        if len(pair) == 2:
            message_pair(pair[0], pair[1])
        elif len(pair) == 3:
            message_trio(pair[0], pair[1], pair[2])


def pair_users():
    reactions = read_reactions()
    unique_users = set(reactions.keys())  # Unique users based on their reactions

    # Logic to randomly shuffle and pair users
    unique_users_list = list(unique_users)
    random.shuffle(unique_users_list)
    pairs = []

    while len(unique_users_list) >= 2:
        pairs.append((unique_users_list.pop(), unique_users_list.pop()))

    # If an odd number of users, handle the last user
    if unique_users_list:
        # Could append to the last pair or create a special case for this user
        if pairs:
            pairs[-1] += (unique_users_list.pop(),)

    # notify users of their pairs
    notify_users(pairs)
    clear_reaction_logs()  # clear the file after pairing


def message_pair(user1, user2):
    slack_app.client.chat_postMessage(channel=user1,
                                      text=f"You've been paired with <@{user2}> for #cds-coffee-roulette! Please arrange a meeting.")
    slack_app.client.chat_postMessage(channel=user2,
                                      text=f"You've been paired with <@{user1}> for #cds-coffee-roulette! Please arrange a meeting.")


def message_trio(user1, user2, user3):
    slack_app.client.chat_postMessage(channel=user1,
                                      text=f"You're in a trio with <@{user2}> and <@{user3}> for #cds-coffee-roulette! Please arrange a meeting.")
    slack_app.client.chat_postMessage(channel=user2,
                                      text=f"You're in a trio with <@{user1}> and <@{user3}> for #cds-coffee-roulette! Please arrange a meeting.")
    slack_app.client.chat_postMessage(channel=user3,
                                      text=f"You're in a trio with <@{user1}> and <@{user2}> for #cds-coffee-roulette! Please arrange a meeting.")

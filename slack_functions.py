import os
import random
import datetime
from dotenv import load_dotenv
from slack_bolt import App
import re
from ai_functions import generate_weekly_message

channel_id = "C06T4HJ4Y5Q"

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
def generate_message_for_week():
    today = datetime.date.today().strftime('%d-%m')
    # Customize this message as needed
    message_content = generate_weekly_message(today)
    print("Message content in generate_weekly_message: " + message_content)
    return message_content


# Function to post the weekly message
def post_weekly_message():
    message_content = generate_message_for_week()
    print("Generated content: " + message_content)

    note = ("\n\n---\n\n_This message was generated and posted by the CDSCoffeeRouletteBot :robot_face: using "
            "generative AI and therefore sometimes my output may be...interesting . For any issues or inquiries, please "
            "contact <@U06T3N4P2M8|josh>_ :josh-nyan-coffee:\n_Known bugs: none_ :smile:")
    message_content += note

    response = slack_app.client.chat_postMessage(channel=channel_id, text=message_content)
    message_ts = response['ts']  # Capture the timestamp of the posted message
    print("Timestamp of posted message: " + message_ts)
    emojis = extract_emojis_from_message(message_content)
    print("Extracted Emojis:", emojis)

    # Check if exactly three emojis are extracted and if not recursively call the function
    if len(emojis) != 3:
        print("Error: Number of extracted emojis is not 3. Retrying...")
        message_content = ""
        post_weekly_message()

    for emoji in emojis:
        print("Adding Emoji", emoji)
        try:
            slack_app.client.reactions_add(
                channel=channel_id,
                name=emoji,
                timestamp=message_ts
            )
        except Exception as e:
            print(f"Error adding reaction {emoji}: {e}")


def extract_emojis_from_message(message_content):
    emoji_pattern = r'^\d\.\s.*:(\w+):'
    emojis_list = re.findall(emoji_pattern, message_content, flags=re.MULTILINE)
    return emojis_list


# Handles the reaction_added event
@slack_app.event("reaction_added")
def handle_reaction_added(event, say):
    user_id = event["user"]
    reaction = event["reaction"]
    # Store the user's reaction
    if reaction in user_responses:
        user_responses[reaction].append(user_id)
    else:
        user_responses[reaction] = [user_id]


# Function to pair users and notify them
def pair_users():
    pairs = []  # This will store tuples of user IDs
    all_unique_users = set()

    # Collect all unique user IDs from reactions
    for users in user_responses.values():
        for user_id in users:
            all_unique_users.add(user_id)

    # Convert the set back to a list for pairing
    unique_users_list = list(all_unique_users)
    random.shuffle(unique_users_list)  # Randomise to avoid bias

    # Pairing logic using the list of unique users
    while len(unique_users_list) >= 2:
        pairs.append((unique_users_list.pop(), unique_users_list.pop()))

    # Handle the case where there's an odd number of users
    if unique_users_list:
        if pairs:
            pairs[random.randint(0, len(pairs) - 1)] += (unique_users_list.pop(),)
        else:
            pairs.append((unique_users_list.pop(),))

    # Notify users of their pairs
    for pair in pairs:
        if len(pair) == 2:
            user1, user2 = pair
            try:
                message_user1 = return_user_message_pair(user2)
                message_user2 = return_user_message_pair(user1)
                slack_app.client.chat_postMessage(channel=user1, text=message_user1)
                slack_app.client.chat_postMessage(channel=user2, text=message_user2)
            except Exception as e:
                print(f"Error sending message to one of the users in the pair {pair}: {e}")
        else:  # Handling a trio
            user1, user2, user3 = pair
            try:
                message_user1 = return_user_message_trio(user2, user3)
                message_user2 = return_user_message_trio(user1, user3)
                message_user3 = return_user_message_trio(user2, user1)
                slack_app.client.chat_postMessage(channel=user1, text=message_user1)
                slack_app.client.chat_postMessage(channel=user2, text=message_user2)
                slack_app.client.chat_postMessage(channel=user3, text=message_user3)
            except Exception as e:
                print(f"Error sending message to one of the users in the trio {pair}: {e}")

    # Reset user_responses for the next round
    user_responses.clear()

def return_user_message_trio(user1, user2):
    return f"You've been paired with <@{user1}> and <@{user2}> for #cds-coffee-roulette! Please arrange a meeting."

def return_user_message_pair(user1):
    return f"You've been paired with <@{user1}> for #cds-coffee-roulette! Please arrange a meeting."
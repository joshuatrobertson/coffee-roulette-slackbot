import os
import random
import datetime
from dotenv import load_dotenv
from slack_bolt import App
import re
from ai_functions import generate_weekly_message
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
def generate_message_for_week():
    today = datetime.date.today().strftime('%d-%m')
    # Customize this message as needed
    message_content = generate_weekly_message(today)
    print("Message content in generate_weekly_message: " + message_content)
    return message_content


# Function to post the weekly message
def post_weekly_message(retry_count=0, max_retries=3):
    if retry_count >= max_retries:
        print(f"Failed to post message after {max_retries} attempts. Emoji addition failed.")
        return  # Exit the function if max retries are reached

    message_content = generate_message_for_week()
    print("Generated content: " + message_content)

    note = ("\n\n---\n\n_This message was generated and posted by the CDSCoffeeRouletteBot :robot_face: using "
            "generative AI and therefore sometimes my output may be...interesting. For any issues or inquiries, please"
            " contact <@U06T3N4P2M8|josh>_ :josh-nyan-coffee:\n_Known bugs: none_ :smile:")
    message_content += note

    response = slack_app.client.chat_postMessage(channel=channel_id, text=message_content)
    message_ts = response['ts']  # Capture the timestamp of the posted message
    store_message_ts(message_ts)  # store it
    print("Timestamp of posted message: " + message_ts)
    emojis = extract_emojis_from_message(message_content)
    print("Extracted Emojis:", emojis)

    if len(emojis) != 3:
        print("Error: Number of extracted emojis is not 3. Retrying...")
        post_weekly_message(retry_count + 1, max_retries)  # Increment the retry count and retry
        return

    failed_to_add_emoji = False
    for emoji in emojis:
        try:
            print("Adding Emoji", emoji)
            slack_app.client.reactions_add(
                channel=channel_id,
                name=emoji,
                timestamp=message_ts
            )
        except Exception as e:
            print(f"Error adding reaction {emoji}: {e}")
            failed_to_add_emoji = True
            break  # Break out of the loop since we need to retry the entire process

    if failed_to_add_emoji:
        try:
            slack_app.client.chat_delete(channel=channel_id, ts=message_ts)  # Attempt to delete the posted message
            print("Deleted message due to emoji addition failure.")
        except Exception as e:
            print(f"Failed to delete message: {e}")

        post_weekly_message(retry_count + 1, max_retries)  # Retry posting the message




def extract_emojis_from_message(message_content):
    emoji_pattern = r'^\d\.\s.*:(\w+):'
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


def log_reaction(user_id, reaction):
    # log the user's reaction to a file
    with open("reactions.txt", "a") as file:
        file.write(f"{user_id},{reaction}\n")
    print(f"Logged reaction {reaction} from user {user_id}")


def read_reactions():
    reactions = {}
    try:
        with open("reactions.txt", "r") as file:
            for line in file:
                user_id, reaction = line.strip().split(',')
                if user_id in reactions:
                    reactions[user_id].append(reaction)
                else:
                    reactions[user_id] = [reaction]
    except FileNotFoundError:
        print("No reactions file found.")
    return reactions


def notify_users(pairs):
    for pair in pairs:
        if len(pair) == 2:
            message_pair(pair[0], pair[1])
        elif len(pair) == 3:
            message_trio(pair[0], pair[1], pair[2])


def return_user_message_trio(user1, user2):
    return f"You've been paired with <@{user1}> and <@{user2}> for #cds-coffee-roulette! Please arrange a meeting."


def return_user_message_pair(user1):
    return f"You've been paired with <@{user1}> for #cds-coffee-roulette! Please arrange a meeting."


def clear_reaction_logs():
    open("reactions.txt", "w").close()


# store the timestamp in timestamp_of_last_post.txt
def store_message_ts(timestamp):
    temp_file_path = ""
    try:
        # Create a temp file
        with tempfile.NamedTemporaryFile(delete=False, mode='w', dir='.') as tmpfile:
            temp_file_path = tmpfile.name
            tmpfile.write(timestamp)

        # Rename temp file replacing the old file
        os.replace(temp_file_path, "timestamp_of_last_post.txt")
    except Exception as e:
        print(f"Failed to write timestamp: {e}")
        # Cleanup if the rename failed
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


# get the weekly timestamp from the last post
def get_current_weekly_message_ts():
    try:
        with open("timestamp_of_last_post.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Timestamp file not found. Ensure the message is posted first.")
        return None
    except IOError as e:
        print(f"Error reading timestamp file: {e}")
        return None


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

import os
import random
import datetime
from dotenv import load_dotenv
from slack_bolt import App

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
    today = datetime.date.today()
    # Customize this message as needed
    message_content = f"What are your Goals/ Resolutions for this week? {today}"
    return message_content


# Function to post the weekly message
def post_weekly_message():
    message_content = generate_message_for_week()
    channel_id = "C06T4HJ4Y5Qe"  # Post to the coffee roulette channel
    print("API call for channel id " + channel_id)
    slack_app.client.chat_postMessage(channel=channel_id, text=message_content)


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
    for reaction, users in user_responses.items():
        random.shuffle(users)  # Randomize to avoid bias
        # Simple pairing logic
        while len(users) >= 2:
            pairs.append((users.pop(), users.pop()))
        if users:  # Handle the case where there's an odd number of users
            if pairs:
                pairs[random.randint(0, len(pairs) - 1)] += (users.pop(),)
            else:  # If no pairs exist and there's only one user
                pairs.append((users.pop(),))

    # Notify users of their pairs
    for pair in pairs:
        for user_id in pair:
            try:
                # You can customize this message
                message = "You've been paired for CDS #coffee-roulette! Please arrange a meeting."
                slack_app.client.chat_postMessage(channel=user_id, text=message)
            except Exception as e:
                print(f"Error sending message to {user_id}: {e}")

    # Reset user_responses for the next round
    user_responses.clear()

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from apscheduler.schedulers.background import BackgroundScheduler
import os
import random
import datetime

# Define the Flask application instance
app = Flask(__name__)

# Define the Slack Bolt app instance
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Create a request handler for Slack events
handler = SlackRequestHandler(slack_app)

# Assuming a simple structure to store user responses. In production, consider using a database.
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
    channel_id = "cds-coffee-roulette"  # Post to the coffee roulette channel
    slack_app.client.chat_postMessage(channel=channel_id, text=message_content)


# Handles the reaction_added event
@slack_app.event("reaction_added")
def handle_reaction_added(event, say):
    user_id = event['user']
    reaction = event['reaction']
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


# Define the route for Slack events
@app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Schedule the post_weekly_message function to run every Monday at 9:00 AM
scheduler.add_job(post_weekly_message, 'cron', day_of_week='mon', hour=9, minute=0)

# Schedule the pair_users function to run every Wednesday at 1:00 PM
scheduler.add_job(pair_users, 'cron', day_of_week='wed', hour=13, minute=0)

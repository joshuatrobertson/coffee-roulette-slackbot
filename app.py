import pytz
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from apscheduler.schedulers.background import BackgroundScheduler
import os
import random
import datetime
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Log the status of environment variables (for verification purposes)
slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
slack_signing_secret = os.getenv('SLACK_SIGNING_SECRET')

if slack_bot_token:
    print("SLACK_BOT_TOKEN is set. First few characters: {}".format(slack_bot_token[:5]))
else:
    print("SLACK_BOT_TOKEN is not set.")

if slack_signing_secret:
    print("SLACK_SIGNING_SECRET is set. First few characters: {}".format(slack_signing_secret[:5]))
else:
    print("SLACK_SIGNING_SECRET is not set.")

# Define the Flask application instance
app = Flask(__name__)

# Define the Slack Bolt app instance
slack_app = App(
    token=slack_bot_token,
    signing_secret=slack_signing_secret
)

# Create a request handler for Slack events
handler = SlackRequestHandler(slack_app)

# Assuming a simple structure to store user responses
user_responses = {}


# Function to generate the weekly message TODO: use GPT
def generate_message_for_week():
    today = datetime.date.today()
    # Customize this message as needed
    message_content = f"What are your Goals/ Resolutions for this week? {today}"
    return message_content


# Function to post the weekly message
def post_weekly_message():
    message_content = generate_message_for_week()
    channel_id = "C06T4HJ4Y5Q"  # Post to the coffee roulette channel
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

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/slack/commands', methods=['POST'])
def slack_commands():
    command_text = request.form['text']
    command = request.form['command']  # The command text (e.g., "/coffee")

    # Check if the command is "/coffee"
    if command == "/coffee":
        # Call the function to generate and post the weekly message
        post_weekly_message()
        # Acknowledge the command without sending a message to the channel
        return jsonify(response_type="ephemeral", text="Coffee message is being posted!")
    else:
        # Handle other commands or provide a default response
        return jsonify({
            "response_type": "ephemeral",  # Only the user who typed the command will see this
            "text": f"Received command '{command}', but I don't know what to do with it."
        })


@app.route('/test', methods=['POST'])
def test():
    return 'It works!', 200


# Initialize the scheduler
scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/London'))
scheduler.start()

# Schedule the post_weekly_message function to run every Monday at 9:00 AM
scheduler.add_job(post_weekly_message, 'cron', day_of_week='mon', hour=9, minute=0)

# Schedule the pair_users function to run every Wednesday at 1:00 PM
scheduler.add_job(pair_users, 'cron', day_of_week='wed', hour=13, minute=0)

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from slack_functions import post_weekly_message, pair_users, handle_reaction_added, delete_last_post, \
    get_last_message_ts

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/health')
def health_check():
    return jsonify(status='ok'), 200


# List of authorized user IDs
AUTHORIZED_USERS = ['U02GDNQPE04']


# Function to check if the user is authorized
def is_user_authorized(user_id):
    return user_id in AUTHORIZED_USERS


@app.route('/slack/commands', methods=['POST'])
def slack_commands():
    user_id = request.form['user_id']
    if not is_user_authorized(user_id):
        return jsonify(response_type="ephemeral", text="You are not authorised to use this command. Please reach out "
                                                       "to <@U02GDNQPE04|josh>")
    command = request.form['command']  # The command text (e.g., "/coffee")
    # Check if the command is "/coffee"
    if command == "/coffee":
        # Call the function to generate and post the weekly message
        post_weekly_message()
        # Acknowledge the command without sending a message to the channel
        return jsonify(response_type="ephemeral", text="Coffee message is being posted!")
    elif command == "/pair":
        # Call the function to pair users
        pair_users()
        # Acknowledge the command without sending a message to the channel
        return jsonify(response_type="ephemeral", text="Users are being paired!")
    elif command == "/delete":
        # Call the function to delete the last post
        delete_last_post()
        # Acknowledge the command without sending a message to the channel
        return jsonify(response_type="ephemeral", text="The last post is being deleted!")
    else:
        # provide a default response
        return jsonify({
            "response_type": "ephemeral",  # Only the user who typed the command will see this
            "text": f"Received command '{command}', but I don't know what to do with it."
        })


# Initialize the scheduler
# scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/London'))
# scheduler.start()

# Schedule the post_weekly_message function to run every Monday at 9:15 AM
# scheduler.add_job(post_weekly_message, 'cron', day_of_week='mon', hour=9, minute=15)


# Schedule the pair_users function to run every Thursday at 1:00 PM
# scheduler.add_job(pair_users, 'cron', day_of_week='wed', hour=13, minute=0)

# Modify to run the post_weekly_message function every day at 9:00 AM TODO: remove when live
# scheduler.add_job(post_weekly_message, 'cron', hour=9, minute=0)

# Modify to run the pair_users function every day at 9:02 AM TODO: remove when live
# scheduler.add_job(pair_users, 'cron', hour=9, minute=2)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from slack_functions import post_weekly_message, pair_users, handle_reaction_added, delete_last_post, \
    get_last_message_ts

app = Flask(__name__)


@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Parse the incoming JSON
    data = request.get_json()

    # Slack sends a challenge request when you add or modify the request URL
    if 'challenge' in data:
        return jsonify({"challenge": data['challenge']})

    # Here, you can handle other events
    # For example, if data contains event information, process it accordingly
    print("Received event:", data)

    # Check if it's a reaction event and call the appropriate function
    if data["event"]["type"] == "reaction_added":
        handle_reaction_added(data)  # Call handle_reaction_event from slack_functions.py
    return "OK", 200


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/health')
def health_check():
    return jsonify(status='ok'), 200


@app.route('/slack/commands', methods=['POST'])
def slack_commands():
    command_text = request.form['text']
    command = request.form['command']  # The command text (e.g., "/coffee")
    print("Received a slash command:", request.form)
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
        # Handle other commands or provide a default response
        return jsonify({
            "response_type": "ephemeral",  # Only the user who typed the command will see this
            "text": f"Received command '{command}', but I don't know what to do with it."
        })


@app.route('/test', methods=['POST'])
def test():
    return 'It works!', 200


# Initialize the scheduler
#scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/London'))
#scheduler.start()

# Schedule the post_weekly_message function to run every Monday at 9:00 AM
# scheduler.add_job(post_weekly_message, 'cron', day_of_week='mon', hour=9, minute=15) TODO: implement when live


# Schedule the pair_users function to run every Wednesday at 1:00 PM
# scheduler.add_job(pair_users, 'cron', day_of_week='wed', hour=13, minute=0) TODO: implement when live

# Modify to run the post_weekly_message function every day at 9:00 AM TODO: remove when live
#scheduler.add_job(post_weekly_message, 'cron', hour=9, minute=0)

# Modify to run the pair_users function every day at 9:02 AM TODO: remove when live
#scheduler.add_job(pair_users, 'cron', hour=9, minute=2)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

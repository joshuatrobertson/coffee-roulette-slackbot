import datetime
from flask import Flask, request, jsonify
from openai_functions import generate_weekly_message
from slack_functions import slack_app, post_weekly_message, pair_users
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

app = Flask(__name__)


# Define the route for Slack events
@app.route("/slack/events", methods=["POST"])
def slack_events():
    return slack_app.dispatch(request)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/health')
def health_check():
    return jsonify(status='ok'), 200


@app.route('/slack/commands', methods=['POST'])
def slack_commands():
    command_text = request.form['text']
    today = datetime.date.today()
    command = request.form['command']
    print("Received a slash command:", request.form)
    if command == "/coffee":
        # Call the function to generate and post the weekly message
        user_prompt = today.strftime()  # Get the user prompt from request or any other source
        message_content = generate_weekly_message(user_prompt)
        # Post the message to Slack
        slack_app.client.chat_postMessage(channel=request.form['channel_id'], text=message_content)
        return jsonify(response_type="ephemeral", text="Coffee message is being posted!")
    else:
        # Handle other commands or provide a default response
        return jsonify({
            "response_type": "ephemeral",
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

if __name__ == '__main__':
    app.run(port=5000)

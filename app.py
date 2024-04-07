import datetime
from flask import Flask, request, jsonify
from slack_functions import slack_app, post_weekly_message, pair_users

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
        message_content = generate_weekly_message(today)
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


if __name__ == '__main__':
    app.run(port=5000)

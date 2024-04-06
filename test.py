import os
from dotenv import load_dotenv

load_dotenv()


# Access environment variables
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")

# Print the values
print("Slack Bot Token:", slack_bot_token)
print("Slack Signing Secret:", slack_signing_secret)
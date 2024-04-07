import os
import openai
import datetime
from dotenv import load_dotenv

load_dotenv()

# Set the OpenAI key
openai.api_key = os.environ["OPENAI"]


def generate_weekly_message():
    today = datetime.date.today()
    prompt = f"What are your Goals/ Resolutions for this week? {today}\n\nResponse:"
    response = openai.Completion.create(
        engine="text-davinci-002",  # Use the GPT model you prefer
        prompt=prompt,
        temperature=0.7,  # Adjust temperature for creativity
        max_tokens=150  # Adjust max_tokens as needed
    )
    message_content = response.choices[0].text.strip()
    return message_content

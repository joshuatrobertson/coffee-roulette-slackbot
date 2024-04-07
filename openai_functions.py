import os
from openai import OpenAI
import datetime
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# Set the OpenAI key
OpenAI.api_key = os.environ["OPENAI"]


def generate_weekly_message():
    today = datetime.date.today()
    prompt = f"What are your Goals/ Resolutions for this week? {today}\n\nResponse:"
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",  # Use the GPT model you prefer
        prompt=prompt,
        top_p=0.3,
        temperature=0.3,  # Adjust temperature for creativity
        max_tokens=2  # Adjust max_tokens as needed
    )
    message_content = response.choices[0].text.strip()
    return message_content

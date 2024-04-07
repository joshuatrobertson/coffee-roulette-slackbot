from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

from transformers import pipeline

generator = pipeline("text-generation", model="gpt-2")

result = generator("Your input prompt here", max_length=50, num_return_sequences=3)


def generate_weekly_message(date):
    return result + date.strftime("%B %d, %Y")

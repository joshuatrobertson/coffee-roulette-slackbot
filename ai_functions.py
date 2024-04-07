import os
import datetime
from dotenv import load_dotenv

load_dotenv()

# Load the pre-trained GPT-2 model and tokenizer
model_name = "gpt2"


def generate_weekly_message(date):
    return "THIS IS A TEST" + date.strftime("%B %d, %Y")

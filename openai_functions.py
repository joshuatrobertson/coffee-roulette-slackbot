import os

import openai
import datetime

from dotenv import load_dotenv

load_dotenv()


# Set your OpenAI API key
openai.api_key = os.environ["OPENAI"]

def generate_weekly_message():

    return "THIS IS A TEST"

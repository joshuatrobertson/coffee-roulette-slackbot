import os
import datetime

from dotenv import load_dotenv

load_dotenv()


def generate_weekly_message(date):
    return "THIS IS A TEST" + date.strftime("%B %d, %Y")

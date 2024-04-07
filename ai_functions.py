from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

text = "Hello, how are you?"
encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors="pt")


def generate_weekly_message(date):
    return encoded_input + date.strftime("%B %d, %Y")

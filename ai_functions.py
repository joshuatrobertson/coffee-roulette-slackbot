from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

from transformers import pipeline

instruct_pipeline = pipeline("text-generation", model="gpt2")

# Generate text
prompt = "Once upon a time"
generated_text = instruct_pipeline(prompt, max_length=150, do_sample=True)


def generate_weekly_message(date):
    return generated_text + date.strftime("%B %d, %Y")

from transformers import GPT2LMHeadModel, GPT2Tokenizer
from dotenv import load_dotenv

load_dotenv()

# Load the pre-trained GPT-2 model and tokenizer
model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)


def generate_weekly_message(date):
    return "THIS IS A TEST" + date.strftime("%B %d, %Y")

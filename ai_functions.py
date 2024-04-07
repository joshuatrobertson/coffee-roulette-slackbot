from transformers import pipeline
import requests

headers = {
    "Authorization": "Bearer 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"
}

data = {
    "inputs": "Introduce yourself",
}

response = requests.post("https://api-inference.huggingface.co/models/gpt2", headers=headers, json=data)
response_list = response.json()  # Assuming this returns a list like [{'generated_text': 'Your text here'}]
# Extract the 'generated_text' from the first item in the list
message_content = response_list[0]['generated_text'] + " " + date.strftime("%B %d, %Y")

def generate_weekly_message(date):
    return message_content + date.strftime("%B %d, %Y")

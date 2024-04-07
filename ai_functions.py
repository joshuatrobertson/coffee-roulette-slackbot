from transformers import pipeline
import requests

headers = {
    "Authorization": "Bearer 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"
}

data = {
    "inputs": "Introduce yourself",
}

response = requests.post("https://api-inference.huggingface.co/models/gpt2", headers=headers, json=data)
print(response.json())


def generate_weekly_message(date):
    return response.json() + date.strftime("%B %d, %Y")

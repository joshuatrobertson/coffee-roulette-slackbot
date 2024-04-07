from transformers import pipeline
import requests
from datetime import datetime  # Import if not already done


def generate_weekly_message(date):
    headers = {
        "Authorization": "Bearer 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"
    }

    prompt = f"Compose an uplifting and motivational message for the team for the week of {date.strftime('%B %d, %Y')}, highlighting the importance of teamwork and looking forward to achieving our goals together."
    data = {
        "inputs": prompt,
    }

    response = requests.post("https://api-inference.huggingface.co/models/gpt2", headers=headers, json=data)

    if response.status_code == 200:
        response_list = response.json()
        if response_list and 'generated_text' in response_list[0]:
            # Extract the 'generated_text' from the first item in the list
            message_content = response_list[0]['generated_text']
            return message_content
        else:
            return "Failed to generate message: unexpected response format."
    else:
        return f"Failed to generate message: HTTP status code {response.status_code}."

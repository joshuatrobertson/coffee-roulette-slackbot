import datetime
import logging

import requests
import os
import json

from data import special_days, seasons

ibm_url = "https://bam-api.res.ibm.com/v2/text/generation?version=2024-03-19"

ibm_api_key = variable_value = os.getenv('IBM_API_KEY')

ibm_header = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {ibm_api_key}'
}


def return_ibm_ai_prompt(prompt):
    # Data payload for the POST request
    data = {
        "model_id": "meta-llama/llama-2-13b-chat",
        "input": prompt,
        "parameters": {
            "decoding_method": "sample",
            "temperature": 0.3,
            "top_p": 0.85,
            "top_k": 20,
            "typical_p": 1,
            "repetition_penalty": 1.05,
            "stop_sequences": [
                "React with your preference, and we'll match you for Coffee Roulette on Thursday!"
            ],
            "include_stop_sequence": True,
            "min_new_tokens": 1,
            "max_new_tokens": 400
        }
    }

    # Convert the data dictionary to a JSON-formatted string
    data_json = json.dumps(data)

    # Make the POST request to the API
    response = requests.post(ibm_url, headers=ibm_header, data=data_json)

    # Check the status code to see if the request was successful
    if response.status_code == 200:
        print("200 Response from IBM API")
        # Parse the JSON response
        response_data = response.json()
        results = response_data.get('results', [])

        # Check if results are available
        if results:
            # Extract 'generated_text' from the first result
            generated_text = results[0].get('generated_text', 'No generated text available.')
            print(f"Generated text: {generated_text}")
            logging.info(f"Generated text: {generated_text}")
            return generated_text


def write_prompt(day):
    instructions = (
        "You are an AI language model. You are helpful and harmless and you follow ethical "
        "guidelines and promote positive behavior. Your outputs must adhere to strict formatting guidelines "
        "without deviating from the user's instructions. You are required to avoid adding any sentences or notes "
        "beyond what is specified by the user. Ensure all responses include only the exact content requested, "
        "with no additional information or notes or any preamble.")
    content = (
        f"Start by generating a Slack post for Coffee Roulette. Your response and the post should begin with 'Good "
        f"Morning AES, it's Monday which means time for #aes-coffee-roulette!' Today is {day} so mention this and ask a fun, related question that asks for a "
        "preference and then provide exactly three answers on new lines that users can vote against. Each answer must start on a new line and end with a contextually relevant single emoji that matches the sentiment or "
        "content of the answer. The answers should be concise, no more than five words each and should include a "
        "number and the answer. The answers should also include a single emoji and adher to the following format. "
        "Here's how the answers should be formatted:\n"
        "1. [First answer to question] [single relevant emoji]\n"
        "2. [Second answer to question] [single relevant emoji]\n"
        "3. [Third answer to question] [single relevant emoji]\n"
        "Conclude with: 'React with your preference, and we'll match you for Coffee Roulette on Thursday!'")
    return f"{instructions} {content}"


def is_first_monday(date, season_start):
    # Check if the date is the first Monday after the season start.
    if date.month == season_start.month and date.day >= season_start.day:
        if date.weekday() == 0:  # Monday
            return date - datetime.timedelta(days=7) < season_start
    return False


def generate_weekly_message():
    event = None
    today = datetime.date.today()

    # Season or first Monday check
    for (month, day), season_name in seasons.items():
        season_start = datetime.date(today.year, month, day)
        if today == season_start or is_first_monday(today, season_start):
            print("Season: " + season_name)
            event = (write_prompt(season_name))
        break

    # Special Day check if not a season event
    if not event:
        today_str = today.strftime('%d-%m')
        event = special_days.get(today_str, '')
        print("Special day: " + event)

    # Construct the prompt
    prompt = (write_prompt(event))
    print("Written prompt: " + prompt)

    return return_ibm_ai_prompt(prompt)


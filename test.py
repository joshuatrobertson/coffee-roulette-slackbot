import os
import re

import emoji
import requests
import json
import logging
import emoji_data_python

from slack_functions import get_slack_emoji_name, emoji_slack_map

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

ibm_url = "https://bam-api.res.ibm.com/v2/text/generation?version=2024-03-19"
ibm_api_key = os.getenv('IBM_API_KEY')

ibm_header = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer pak-vYsLLW6x0etpV5_gv4P-v1YZ_k9viZz5PwNttYrli2U'  # Using the variable for API key
}


def write_prompt(day):
    instructions = (
        "You are an AI language model developed by IBM. You are helpful and harmless and you follow ethical "
        "guidelines and promote positive behavior. Your outputs must adhere to strict formatting guidelines "
        "without deviating from the user's instructions. You are required to avoid adding any sentences or notes "
        "beyond what is specified by the user. Ensure all responses include only the exact content requested, "
        "with no additional information or notes or any preamble.")
    content = (
        f"Start by generating a Slack post for Coffee Roulette. Your response and the post should begin with 'Good "
        f"Morning CDS, it's Monday which means time for #cds-coffee-roulette!' Today is {day} so mention this and ask a fun, related question that asks for a "
        "preference and then provide exactly three answers on new lines that users can vote against. Each answer must start on a new line and end with a contextually relevant emoji that matches the sentiment or "
        "content of the answer. The answers should be concise, no more than five words each and should include a "
        "number and the answer. The answers should also include a single emoji and adher to the following format. "
        "Here's how the answers should be formatted:\n"
        "1. [First answer to question] [single relevant emoji]\n"
        "2. [Second answer to question] [single relevant emoji]\n"
        "3. [Third answer to question] [single relevant emoji]\n"
        "Conclude with: 'React with your preference, and we'll match you for Coffee Roulette on Thursday!'")
    return f"{instructions} {content}"


def extract_emojis_from_message(message_content):
    print("Extracting emojis..")
    emojis_in_message = []
    try:
        for line in message_content.split('\n'):
            if re.match(r'^[1-3]\.', line.strip()):
                # Extract emojis from each line and convert them to Slack names
                slack_emojis = [get_slack_emoji_name(char) for char in line if char in emoji_slack_map]
                print(f"Found emojis: {slack_emojis}")
                emojis_in_message.extend(slack_emojis)
        return emojis_in_message
    except Exception as e:  # Broadening error handling to catch all exceptions
        logging.error(f"Failed to extract emojis due to: {str(e)}")
        return []


data = {
    "model_id": "meta-llama/llama-2-13b-chat",
    "input": write_prompt('Christmas'),
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

response = requests.post(ibm_url, headers=ibm_header, data=json.dumps(data))

if response.status_code != 200:
    logging.error(f"Non-200 status code received: {response.status_code}")
    logging.error(f"Response Body: {response.text}")
else:
    logging.info("200 Response from IBM API")
    response_data = response.json()
    results = response_data.get('results', [])
    if results:
        generated_text = results[0].get('generated_text', 'No generated text available.')
        print(f"generated text: {generated_text}")
        emojis = extract_emojis_from_message(generated_text)
        for e in emojis:
            print(f"Emoji : {e}")

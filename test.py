import os
import re

import requests
import json
import logging
import emoji

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

ibm_url = "https://bam-api.res.ibm.com/v2/text/generation?version=2024-03-19"
ibm_api_key = os.getenv('IBM_API_KEY')

ibm_header = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer pak-vYsLLW6x0etpV5_gv4P-v1YZ_k9viZz5PwNttYrli2U'
}


def write_prompt(day):
    instructions = (
        "You are an AI language model developed by IBM. You are helpful and harmless and you follow ethical "
        "guidelines and promote positive behavior. Your outputs must adhere to strict formatting guidelines "
        "without deviating from the user's instructions. You are required to avoid adding any sentences or notes "
        "beyond what is specified by the user. Ensure all responses include only the exact content requested, "
        "with no additional information or notes or any preamble."
    )
    content = (
        f"Start by generating a Slack post for Coffee Roulette. Your response and the post should begin with 'Good Morning CDS, it's Monday which means time for "
        f"#cds-coffee-roulette!' Today is {day} so mention this and ask a fun, related question that asks for a preference and then provide exactly three answers on new lines. "
        "Each answer must start on a new line and end with a contextually relevant emoji that matches the sentiment or "
        "content of the answer. The answers should be concise, no more than five words each and should include a "
        "number, the answer. The answers should also include a single emoji and adher to the following format. Here's how the answers should be formatted:\n"
        "1. [First answer to question] [single relevant emoji]\n"
        "2. [Second answer to question] [single relevant emoji]\n"
        "3. [Third answer to question] [single relevant emoji]\n"
        "Conclude with: 'React with your preference, and we'll match you for Coffee Roulette on Thursday!'"
    )
    return f"{instructions} {content}"

# Extract emojiis where the line starts with a number

def extract_emojis_from_message(message_content):
    try:
        emojis_in_message = []
        # Split the message into lines and process each line
        for line in message_content.split('\n'):
            # Check if the line starts with '1.', '2.', or '3.'
            if re.match(r'^[1-3]\.', line.strip()):
                # Extract emojis from the line if it matches
                emojis_in_line = [char for char in line if char in emoji.EMOJI_DATA]
                emojis_in_message.extend(emojis_in_line)
        return emojis_in_message
    except AttributeError as e:
        logging.error(f"Failed to extract emojis due to: {str(e)}")
        # Handle the error or use a fallback method
        return []


data = {
    "model_id": "ibm/granite-13b-lab-incubation",
    "input": write_prompt('National Do No Housework Day'),
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
    logging.error(f"Response Body: {response.text}")  # Log the error message from the API
else:
    logging.info("200 Response from IBM API")
    response_data = response.json()
    results = response_data.get('results', [])
    if results:
        generated_text = results[0].get('generated_text', 'No generated text available.')
        print(f"generated text: {generated_text}")
        emojis = extract_emojis_from_message(generated_text)
        for e in emojis:
            print(e)



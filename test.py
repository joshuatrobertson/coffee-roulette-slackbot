import os
from dotenv import load_dotenv
from slack_functions import extract_emojis_from_message

test_message = "Hello there!\n1: :smile:\n2: :coffee:\n3: :robot_face:"
extracted_emojis = extract_emojis_from_message(test_message)
print(extracted_emojis)
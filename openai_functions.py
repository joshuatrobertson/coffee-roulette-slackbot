import os
import google.generativeai as genai
import datetime
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# Set the OpenAI key

# Set variables
temperature = 0.2
max_tokens = 256
frequency_penalty = 0.0


def generate_weekly_message(user_prompt):
    today = datetime.date.today()
    assistant_prompt = (
        "Your role is to help users create engaging and friendly Slack posts for organizing coffee "
        "roulette sessions within their teams or organizations. Your posts start with a brief "
        "greeting, such as 'Good Morning CDS and happy Monday!' without mentioning the full date, "
        "setting a consistent and inviting tone. The opening line encourages participation in the "
        "week's #coffee-roulette with a short message. When creating posts, maintain a balanced "
        "tone that is both playful and professional to foster a welcoming community spirit while "
        "keeping the message clear and organized. Each post includes one question related to "
        "lighthearted topics or themes relevant to the current date, with three emoji-reactable "
        "answers. Emojis are placed before each short, single-line answer, inviting users to "
        "engage by reacting. After presenting the question and answers, post a short closing line "
        "that ties back to the theme of the question or the spirit of coffee roulette. Make sure "
        "that there is only one closing sentence after the answers. Avoid generating content that "
        "could be seen as overly formal or corporate, promoting informal and friendly "
        "interactions instead. Never ask questions back, always just provide the output. ")

    response = model.generate_content(assistant_prompt + ". Todays date is " + today)

    message_content = response.choices[0].text.strip()
    return message_content

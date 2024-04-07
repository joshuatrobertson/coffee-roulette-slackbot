import os
from openai import OpenAI
import datetime
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# Set the OpenAI key
OpenAI.api_key = os.environ["OPENAI"]

# Set variables
temperature = 0.2
max_tokens = 256
frequency_penalty = 0.0


def generate_weekly_message(user_prompt):
    today = datetime.date.today()
    gpt_assistant_prompt = (
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
        "interactions instead. Never ask questions back, always just provide the output. "
        f"Who should I be, as I answer your prompt? {user_prompt}")

    message = [{"role": "assistant", "content": gpt_assistant_prompt}]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=message,
        temperature=temperature,
        max_tokens=max_tokens,
        frequency_penalty=frequency_penalty
    )

    message_content = response.choices[0].text.strip()
    return message_content

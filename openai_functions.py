import openai
import datetime


load_dotenv()


# Set your OpenAI API key
openai.api_key = 'your-api-key'

def generate_weekly_message():
    today = datetime.date.today()
    prompt = f"What are your Goals/ Resolutions for this week? {today}\n\nResponse:"
    response = openai.Completion.create(
        engine="text-davinci-002",  # Use the GPT model you prefer
        prompt=prompt,
        temperature=0.7,  # Adjust temperature for creativity
        max_tokens=150  # Adjust max_tokens as needed
    )
    message_content = response.choices[0].text.strip()
    return message_content

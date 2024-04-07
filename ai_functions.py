import cohere

# Initialize the Cohere client with your API key
cohere_client = cohere.Client(api_key="uoQSq5wxhvw4bTa8hjLBWuQast6AqmeHWvONfdy3")


def generate_weekly_message(date):
    # Your existing function logic here
    prompt = f"On {date}, we accomplished the following:"

    # Generate text using Cohere's language model
    generated_text = cohere_client.generate(prompt, length=100)

    return generated_text
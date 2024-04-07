import cohere

# Initialize the Cohere client with your API key
cohere_client = cohere.Client('uoQSq5wxhvw4bTa8hjLBWuQast6AqmeHWvONfdy3')


def generate_weekly_message(date):
    # Your existing function logic here
    prompt = f"On {date}, we accomplished the following:"

    # Generate text using Cohere's language model
    # Specify the model, prompt, and any other parameters as needed
    response = cohere_client.generate(
        model='large',  # Example model, choose the appropriate one for your use case
        prompt=prompt,
        max_tokens=50,  # Example token count, adjust as necessary
        temperature=0.5  # Example creativity setting, adjust as needed
    )

    # Extracting the generated text from the response
    generated_text = response.text

    return generated_text

import cohere

# Initialize the Cohere client with your API key
co = cohere.Client('uoQSq5wxhvw4bTa8hjLBWuQast6AqmeHWvONfdy3')


def generate_weekly_message(date):
    # Your existing function logic here
    prompt = (f"Your role is to help users create engaging and friendly Slack posts for organizing coffee roulette "
              f"sessions within their teams or organizations. Your posts start with a brief greeting, such as 'Good "
              f"Morning CDS and happy Monday!' without mentioning the full date, setting a consistent and inviting "
              f"tone. The opening line encourages participation in the week's #coffee-roulette with a short message. "
              f"When creating posts, maintain a balanced tone that is both playful and professional to foster a "
              f"welcoming community spirit while keeping the message clear and organized. Each post includes one "
              f"question related to lighthearted topics or themes relevant to the current date for example if the "
              f"date is in december you could write something about chistmas, with three"
              f"emoji-reactable answers. Emojis are placed before each short, single-line answer, inviting users to "
              f"engage by reacting. After presenting the question and answers, post a short closing line that says "
              f"something like 'Get reacting and I'll let you know when it's time to match you with a co-worker for a "
              f"coffee chat!' Make sure that there is only one"
              f"closing sentence after the answers. Avoid generating content that could be seen as overly formal or "
              f"corporate, promoting informal and friendly interactions instead. Never ask questions back, "
              f"always just provide the output. The current date is: " + date)

    # Generate text using Cohere's language model
    # Specify the model, prompt, and any other parameters as needed
    response = co.generate(
        model='command',  # Example model, choose the appropriate one for your use case
        prompt=prompt,
        max_tokens=150,  # Example token count, adjust as necessary
        temperature=0.5  # Example creativity setting, adjust as needed
    )

    # Extracting the generated text from the response
    generated_text = response.generations[0].text

    return generated_text

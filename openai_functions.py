import datetime
from transformers import GPT2LMHeadModel, GPT2Tokenizer

def generate_weekly_message():
    # Load pre-trained GPT-2 model and tokenizer
    model_name = "gpt2-medium"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)

    # Define the prompt
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
        "interactions instead. Never ask questions back, always just provide the output. "
    )

    # Generate content using the model
    input_text = assistant_prompt + f" Today's date is {today}."
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output = model.generate(input_ids, max_length=150, num_return_sequences=1, temperature=0.7)

    # Decode the generated text and return it
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text

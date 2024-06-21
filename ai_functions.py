import datetime
import logging
import requests
import os
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)

ibm_url = "https://bam-api.res.ibm.com/v2/text/generation?version=2024-03-19"




def return_ibm_ai_prompt(prompt):
    ibm_api_key = os.getenv('IBM_API_KEY')
    ibm_header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ibm_api_key}'
    }

    logging.debug(f"Generating prompt with IBM AI with bearer {ibm_api_key}")
    data = {
        "model_id": "meta-llama/llama-2-13b-chat",
        "input": prompt,
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
    data_json = json.dumps(data)
    response = requests.post(ibm_url, headers=ibm_header, data=data_json)

    if response.status_code == 200:
        logging.info("200 Response from IBM API")
        response_data = response.json()
        results = response_data.get('results', [])
        if results:
            generated_text = results[0].get('generated_text', 'No generated text available.')
            logging.info(f"Generated text: {generated_text}")
            return generated_text
    else:
        logging.error(f"Error from IBM API: {response.status_code} - {response.text}")
    return None

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

def is_first_monday(date, season_start):
    if date.month == season_start.month and date.day >= season_start.day:
        if date.weekday() == 0:
            return date - datetime.timedelta(days=7) < season_start
    return False

def generate_weekly_message():
    event = None
    today = datetime.date.today()
    logging.debug(f"Today's date: {today}")

    today_str = today.strftime('%d-%m')
    event = special_days.get(today_str, '')
    logging.info(f"Special day: {event}")

    prompt = write_prompt(event)
    logging.debug(f"Generated prompt: {prompt}")

    response = return_ibm_ai_prompt(prompt)
    if response is None:
        logging.error("Failed to generate message from IBM API")
        return "Failed to generate message"

    return response


special_days = {
    '01-01': "New Years Day",
    '02-01': "Science Fiction Day",
    '03-01': "Festival of Sleep Day",
    '04-01': "National Trivia Day",
    '05-01': "National Bird Day",
    '06-01': "National Shortbread Day",
    '07-01': "Old Rock Day",
    '08-01': "Bubble Bath Day",
    '09-01': "Static Electricity Day",
    '10-01': "Houseplant Appreciation Day",
    '11-01': "Learn Your Name in Morse Code Day",
    '12-01': "Marzipan Day",
    '13-01': "Rubber Ducky Day",
    '14-01': "Dress Up Your Pet Day",
    '15-01': "National Hat Day",
    '16-01': "Appreciate a Dragon Day",
    '17-01': "Ditch New Year's Resolutions Day",
    '18-01': "Winnie the Pooh Day",
    '19-01': "Popcorn Day",
    '21-01': "Squirrel Appreciation Day",
    '23-01': "Handwriting Day",
    '25-01': "Opposite Day",
    '26-01': "International Day of Clean Energy",
    '27-01': "Chocolate Cake Day",
    '29-01': "Puzzle Day",
    '30-01': "Croissant Day",
    '31-01': "Backward Day",
    '01-02': "Serpent Day",
    '03-02': "Carrot Cake Day",
    '05-02': "World Nutella Day",
    '06-02': "Frozen Yogurt Day",
    '07-02': "Send a Card to a Friend Day",
    '10-02': "Umbrella Day",
    '11-02': "Make a Friend Day",
    '12-02': "Plum Pudding Day",
    '15-02': "Singles Awareness Day",
    '16-02': "Innovation Day",
    '17-02': "Random Acts of Kindness Day",
    '18-02': "Battery Day",
    '19-02': "Chocolate Mint Day",
    '21-02': "Sticky Bun Day",
    '23-02': "Banana Bread Day",
    '24-02': "Tortilla Chip Day",
    '25-02': "National Chocolate Covered Nut Day",
    '26-02': "Tell a Fairy Tale Day",
    '27-02': "Strawberry Day",
    '28-02': "Tooth Fairy Day",
    '01-03': "Pig Day",
    '02-03': "Old Stuff Day",
    '03-03': "What If Cats and Dogs Had Opposable Thumbs Day,",
    '04-03': "Grammar Day",
    '05-03': "Cheese Doodle Day",
    '06-03': "Dentist’s Day",
    '07-03': "Cereal Day",
    '08-03': "International Women's Day",
    '09-03': "Meatball Day",
    '10-03': "Mario Day",
    '11-03': "Worship of Tools Day",
    '12-03': "Plant a Flower Day",
    '13-03': "Jewel Day",
    '14-03': "Pi Day",
    '15-03': "Ides of March",
    '16-03': "Everything You Do is Right Day",
    '17-03': "St. Patrick's Day",
    '18-03': "Global Recycling Day",
    '19-03': "Let's Laugh Day",
    '20-03': "International Day of Happiness",
    '21-03': "World Poetry Day",
    '22-03': "World Water Day",
    '23-03': "Puppy Day",
    '24-03': "Chocolate Covered Raisin Day",
    '25-03': "Waffle Day",
    '26-03': "Make Up Your Own Holiday Day",
    '27-03': "Spanish Paella Day",
    '28-03': "Something on a Stick Day",
    '29-03': "Knights of Ni Day",
    '30-03': "Pencil Day",
    '31-03': "Crayon Day",
    '01-04': "April Fool's Day",
    '02-04': "Peanut Butter and Jelly Day",
    '03-04': "Find a Rainbow Day",
    '04-04': "National Burrito Day",
    '05-04': "Read a Road Map Day",
    '06-04': "Caramel Popcorn Day",
    '07-04': "No Housework Day",
    '08-04': "Draw a Picture of a Bird Day",
    '09-04': "Name Yourself Day",
    '10-04': "Golfer’s Day",
    '11-04': "Pet Day",
    '12-04': "Grilled Cheese Sandwich Day",
    '13-04': "Scrabble Day",
    '14-04': "Look Up at the Sky Day",
    '15-04': "Titanic Remembrance Day",
    '16-04': "Wear Pajamas to Work Day",
    '17-04': "Haiku Poetry Day",
    '18-04': "Amateur Radio Day",
    '19-04': "Garlic Day",
    '20-04': "Look Alike Day",
    '21-04': "Tea Day",
    '22-04': "Earth Day",
    '23-04': "Talk Like Shakespeare Day",
    '24-04': "Pig in a Blanket Day",
    '25-04': "DNA Day",
    '26-04': "Pretzel Day",
    '27-04': "Tell a Story Day",
    '28-04': "Superhero Day",
    '29-04': "International Dance Day",
    '30-04': "Honesty Day",
    '01-05': "May Day",
    '02-05': "Baby Day",
    '03-05': "World Press Freedom Day",
    '04-05': "Star Wars Day",
    '05-05': "Cinco de Mayo",
    '06-05': "International No Diet Day",
    '07-05': "National Cosmopolitan Day",
    '08-05': "No Socks Day",
    '09-05': "Lost Sock Memorial Day",
    '10-05': "Clean Up Your Room Day",
    '11-05': "Eat What You Want Day",
    '12-05': "Limerick Day",
    '13-05': "Frog Jumping Day",
    '14-05': "Dance Like a Chicken Day",
    '15-05': "Chocolate Chip Day",
    '16-05': "Wear Purple for Peace Day",
    '17-05': "Pack Rat Day",
    '18-05': "No Dirty Dishes Day",
    '19-05': "May Ray Day",
    '20-05': "Be a Millionaire Day",
    '21-05': "Talk Like Yoda Day",
    '22-05': "Buy a Musical Instrument Day",
    '23-05': "Lucky Penny Day",
    '24-05': "Scavenger Hunt Day",
    '25-05': "Towel Day",
    '26-05': "World Dracula Day",
    '27-05': "Sunscreen Day",
    '28-05': "Hamburger Day",
    '29-05': "Put a Pillow on Your Fridge Day",
    '30-05': "Water a Flower Day",
    '31-05': "World No Tobacco Day",
    '01-06': "Say Something Nice Day",
    '02-06': "Rocky Road Day",
    '03-06': "Repeat Day (I said, ""Repeat Day"")",
    '04-06': "Hug Your Cat Day",
    '05-06': "World Environment Day",
    '06-06': "Yo-Yo Day",
    '07-06': "Chocolate Ice Cream Day",
    '08-06': "Best Friends Day",
    '09-06': "Donald Duck Day",
    '10-06': "Iced Tea Day",
    '11-06': "Corn on the Cob Day",
    '12-06': "Red Rose Day",
    '13-06': "Sewing Machine Day",
    '14-06': "World Blood Donor Day",
    '15-06': "Smile Power Day",
    '16-06': "Fresh Veggies Day",
    '17-06': "Eat Your Vegetables Day",
    '18-06': "Go Fishing Day",
    '19-06': "Martini Day",
    '20-06': "World Juggling Day",
    '21-06': "Selfie Day",
    '22-06': "Onion Rings Day",
    '23-06': "Pink Day",
    '24-06': "National Take Back the Lunch Break Day",
    '25-06': "Log Cabin Day",
    '26-06': "Chocolate Pudding Day",
    '27-06': "Sunglasses Day",
    '28-06': "CAPS LOCK DAY",
    '29-06': "Camera Day",
    '30-06': "Meteor Watch Day",
    '01-07': "International Joke Day",
    '02-07': "World UFO Day",
    '03-07': "Stay Out of the Sun Day",
    '04-07': "Independence Day (USA)",
    '05-07': "Apple Turnover Day",
    '06-07': "National Hand Roll Day",
    '07-07': "World Chocolate Day",
    '08-07': "Video Games Day",
    '09-07': "Sugar Cookie Day",
    '10-07': "Teddy Bear Picnic Day",
    '11-07': "Cheer Up the Lonely Day",
    '12-07': "Different Colored Eyes Day",
    '13-07': "Embrace Your Geekness Day",
    '14-07': "Pandemonium Day",
    '15-07': "Give Something Away Day",
    '16-07': "World Snake Day",
    '17-07': "World Emoji Day",
    '18-07': "Nelson Mandela International Day",
    '19-07': "National Raspberry Cake Day",
    '20-07': "Space Exploration Day",
    '21-07': "National Junk Food Day",
    '22-07': "Hammock Day",
    '23-07': "Vanilla Ice Cream Day",
    '24-07': "Tell an Old Joke Day",
    '25-07': "Thread the Needle Day",
    '26-07': "All or Nothing Day",
    '27-07': "National Cowboy Day",
    '28-07': "Milk Chocolate Day",
    '29-07': "Lipstick Day",
    '30-07': "International Friendship Day",
    '31-07': "Mutt Day",
    '01-08': "Respect for Parents Day",
    '02-08': "Ice Cream Sandwich Day",
    '03-08': "Watermelon Day",
    '04-08': "Coast Guard Day",
    '05-08': "National Oyster Day",
    '06-08': "Wiggle Your Toes Day",
    '07-08': "Lighthouse Day",
    '08-08': "International Cat Day",
    '09-08': "Book Lovers Day",
    '10-08': "Lazy Day",
    '11-08': "Play in the Sand Day",
    '12-08': "Middle Child's Day",
    '13-08': "Left Handers Day",
    '14-08': "Creamsicle Day",
    '15-08': "Relaxation Day",
    '16-08': "Tell a Joke Day",
    '17-08': "Thrift Shop Day",
    '18-08': "Bad Poetry Day",
    '19-08': "World Photo Day",
    '20-08': "Chocolate Pecan Pie Day",
    '21-08': "Senior Citizens Day",
    '22-08': "Be an Angel Day",
    '23-08': "Ride the Wind Day",
    '24-08': "Peach Pie Day",
    '25-08': "Banana Split Day",
    '26-08': "Dog Day",
    '27-08': "Just Because Day",
    '28-08': "Bow Tie Day",
    '29-08': "Lemon Juice Day",
    '30-08': "Toasted Marshmallow Day",
    '31-08': "Eat Outside Day",
    '01-09': "Letter Writing Day",
    '02-09': "Blueberry Popsicle Day",
    '03-09': "Skyscraper Day",
    '04-09': "Eat an Extra Dessert Day",
    '05-09': "Cheese Pizza Day",
    '06-09': "Read a Book Day",
    '07-09': "Buy a Book Day",
    '08-09': "Star Trek Day",
    '09-09': "Teddy Bear Day",
    '10-09': "Swap Ideas Day",
    '11-09': "Make Your Bed Day",
    '12-09': "Chocolate Milkshake Day",
    '13-09': "Positive Thinking Day",
    '14-09': "Eat a Hoagie Day",
    '15-09': "Make a Hat Day",
    '16-09': "Collect Rocks Day",
    '17-09': "Apple Dumpling Day",
    '18-09': "Cheeseburger Day",
    '19-09': "Talk Like a Pirate Day",
    '20-09': "Pepperoni Pizza Day",
    '21-09': "International Peace Day",
    '22-09': "Ice Cream Cone Day",
    '23-09': "Checkers Day",
    '24-09': "Punctuation Day",
    '25-09': "Comic Book Day",
    '26-09': "Pancake Day",
    '27-09': "Tourism Day",
    '28-09': "Drink Beer Day",
    '29-09': "Coffee Day",
    '30-09': "Hot Mulled Cider Day",
    '01-10': "International Coffee Day",
    '02-10': "Name Your Car Day",
    '03-10': "Boyfriend's Day",
    '04-10': "Taco Day",
    '05-10': "Do Something Nice Day",
    '06-10': "Noodle Day",
    '07-10': "Bathtub Day",
    '08-10': "Octopus Day",
    '09-10': "Moldy Cheese Day",
    '10-10': "Handbag Day",
    '11-10': "Sausage Pizza Day",
    '12-10': "Farmers Day",
    '13-10': "Yorkshire Pudding Day",
    '14-10': "Dessert Day",
    '15-10': "Mushroom Day",
    '16-10': "Dictionary Day",
    '17-10': "National Pasta Day",
    '18-10': "Chocolate Cupcake Day",
    '19-10': "Seafood Bisque Day",
    '20-10': "Suspender Day",
    '21-10': "Count Your Buttons Day",
    '22-10': "Colour Day",
    '23-10': "Horror Movie Day",
    '24-10': "Bologna Day",
    '25-10': "Pasta Day",
    '26-10': "Pumpkin Day",
    '27-10': "Black Cat Day",
    '28-10': "Animation Day",
    '29-10': "Internet Day",
    '30-10': "Checklist Day",
    '31-10': "Halloween",
    '01-11': "Authors' Day",
    '02-11': "Deviled Egg Day",
    '03-11': "Sandwich Day",
    '04-11': "Candy Day",
    '05-11': "Doughnut Day",
    '06-11': "Nachos Day",
    '07-11': "Hug a Bear Day",
    '08-11': "Cappuccino Day",
    '09-11': "Chaos Never Dies Day",
    '10-11': "Forget-Me-Not Day",
    '11-11': "Origami Day",
    '12-11': "Pizza with the Works Except Anchovies Day",
    '13-11': "World Kindness Day",
    '14-11': "Pickle Day",
    '15-11': "Clean Out Your Refrigerator Day",
    '16-11': "Fast Food Day",
    '17-11': "Take a Hike Day",
    '18-11': "Mickey Mouse Day",
    '19-11': "Play Monopoly Day",
    '20-11': "Children's Day",
    '21-11': "Hello Day",
    '22-11': "Go For a Ride Day",
    '23-11': "Espresso Day",
    '24-11': "Celebrate Your Unique Talent Day",
    '25-11': "Parfait Day",
    '26-11': "Cake Day",
    '27-11': "Pins and Needles Day",
    '28-11': "French Toast Day",
    '29-11': "Electronic Greeting Card Day",
    '30-11': "Computer Security Day",
    '01-12': "Eat a Red Apple Day",
    '02-12': "Fritters Day",
    '03-12': "Roof Over Your Head Day",
    '04-12': "Cookie Day",
    '05-12': "National Sacher Torte Day",
    '06-12': "Put on Your Own Shoes Day",
    '07-12': "Letter Writing Day",
    '08-12': "Brownie Day",
    '09-12': "Pastry Day",
    '10-12': "Dewey Decimal System Day",
    '11-12': "Noodle Day",
    '12-12': "Poinsettia Day",
    '13-12': "Ice Cream Day",
    '14-12': "Monkey Day",
    '15-12': "Tea Day",
    '16-12': "Chocolate Covered Anything Day",
    '17-12': "Maple Syrup Day",
    '18-12': "Bake Cookies Day",
    '19-12': "Oatmeal Muffin Day",
    '20-12': "Sangria Day",
    '21-12': "Crossword Puzzle Day",
    '22-12': "Date Nut Bread Day",
    '23-12': "Festivus",
    '24-12': "Eggnog Day",
    '25-12': "Christmas Day",
    '26-12': "Candy Cane Day",
    '27-12': "Fruitcake Day",
    '28-12': "Card Playing Day",
    '29-12': "Tick Tock Day",
    '30-12': "Bacon Day",
    '31-12': "New Years Eve",
}

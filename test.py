import os
from dotenv import load_dotenv

# Assuming your .env file is in the same directory as your script
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Load the .env file
load_dotenv(dotenv_path)

# Attempt to fetch the IBM API Key from environment variables
ibm_api_key = os.getenv("IBM_API_KEY")

# Debugging: Log the value of IBM_API_KEY
print("IBM API Key:", ibm_api_key)
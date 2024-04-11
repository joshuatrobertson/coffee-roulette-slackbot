import os

# Attempt to fetch the IBM API Key from environment variables
ibm_api_key = os.getenv("IBM_ASSISTANT_ID")

# Debugging: Log the value of IBM_API_KEY
print("IBM API Key:", ibm_api_key)

# Ensure the IBM API Key is present before proceeding
if not ibm_api_key:
    raise ValueError("The IBM_API_KEY environment variable is missing or not set.")
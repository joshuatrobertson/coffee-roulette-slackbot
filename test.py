import requests
import json

api = 'pak-vYsLLW6x0etpV5_gv4P-v1YZ_k9viZz5PwNttYrli2U'

# Define the URL for the API
url = "https://bam-api.res.ibm.com/v2/text/generation?version=2024-03-19"

# Create the headers with the Content-Type and Authorization
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api}'  # Replace ****** with your actual bearer token
}

# Define the data payload
data = {
    "model_id": "google/flan-ul2",
    "input": "Write a tagline for an alumni association: Together we",
    "parameters": {
        "temperature": 0,
        "max_new_tokens": 3
    }
}

# Convert the data dictionary to a JSON-formatted string
data_json = json.dumps(data)

# Make the POST request to the API
response = requests.post(url, headers=headers, data=data_json)

# Check the status code to see if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    response_data = response.json()

    # Access the 'results' part of the data
    results = response_data.get('results', [])

    # Check if results are available
    if results:
        # Extract 'generated_text' from the first result
        generated_text = results[0].get('generated_text', 'No generated text available.')
        print("Generated text:", generated_text)
    else:
        print("No results found in the response.")
else:
    # Print an error message if the request failed
    print("Failed to retrieve data:", response.status_code, response.text)

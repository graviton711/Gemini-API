import requests
import json

# URL of your local proxy
url = "http://localhost:8000/v1beta/models/gemini-1.5-flash:generateContent"

# Payload for the request
payload = {
    "contents": [{
        "parts": [{"text": "Hello, explain how AI works in one sentence."}]
    }]
}

headers = {
    "Content-Type": "application/json"
}

print(f"Sending request to {url}...")

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("Response:")
        print(response.text)
    else:
        print("Error:")
        print(response.text)

except Exception as e:
    print(f"An error occurred: {e}")

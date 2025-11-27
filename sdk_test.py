from google import genai
from google.genai import types
import os

# Configure the client to use the local proxy
# We need to set the API key (can be dummy if proxy handles it, but SDK might validate)
# And the base URL.
# For google-genai v0.1+, we might need to use `client_options` or similar.
# Let's try to find the correct way. 
# If we can't find it, we'll try setting `api_endpoint` in `Client`.

# Note: The proxy rotates keys, so we don't strictly need a valid key here 
# IF the proxy replaces it. But the SDK requires one.
# We'll use a dummy key.
os.environ["GOOGLE_API_KEY"] = "dummy_key"

try:
    # Attempt to configure base_url. 
    # Based on common patterns, it might be `http_options={'api_endpoint': ...}`
    # or just `client = genai.Client(http_options={'api_endpoint': 'http://localhost:8000'})`
    
    # Let's try the most likely configuration for this new SDK.
    # If this fails, we will need to research or inspect the SDK.
    
    client = genai.Client(
        http_options={'base_url': 'http://localhost:8000'}
    )

    print("Sending request via SDK...")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Explain how AI works in a few words",
    )

    print("Response received:")
    print(response.text)

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"SDK Test Failed: {e}")

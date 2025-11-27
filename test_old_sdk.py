import google.generativeai as genai
import os

# Configure the SDK to use the local proxy
os.environ["GOOGLE_API_KEY"] = "dummy_key"

# Configure the client with the local endpoint
# Note: google-generativeai uses 'client_options' with 'api_endpoint'
genai.configure(
    transport="rest",
    client_options={"api_endpoint": "http://localhost:8000"}
)

try:
    print("Creating model...")
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    print("Generating content...")
    response = model.generate_content("Hôm nay là ngày bao nhiêu?")
    
    print("Response received:")
    print(response.text)

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Old SDK Test Failed: {e}")

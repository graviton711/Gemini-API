import google.generativeai as genai
import os

# Configure the SDK to use the local proxy
os.environ["GOOGLE_API_KEY"] = "dummy_key"

genai.configure(
    transport="rest",
    client_options={"api_endpoint": "https://gemini-ptn7u4294-thaisonphandang0711-6295s-projects.vercel.app"}
)

try:
    model = genai.GenerativeModel('gemini-2.5-pro')
    response = model.generate_content("Hôm nay là ngày bao nhiêu?")
    print(response.text)

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Old SDK Test Failed: {e}")

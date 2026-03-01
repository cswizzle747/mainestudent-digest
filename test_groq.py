import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{
        "role": "user",
        "content": "Say hello and tell me a fun fact about Portland, Maine in 2 sentences."
    }]
}

print("Testing Groq API...")
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    text = result["choices"][0]["message"]["content"]
    print("✅ It works!\n")
    print(f"AI says: {text}")
else:
    print(f"❌ Error! Status code: {response.status_code}")
    print(response.text)
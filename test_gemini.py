# test_gemini.py
# Quick test to make sure your Gemini API key works

import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

headers = {"Content-Type": "application/json"}

data = {
    "contents": [{
        "parts": [{
            "text": "Say hello and tell me a fun fact about Portland, Maine in 2 sentences."
        }]
    }]
}

print("Testing Gemini API...")
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    text = result["candidates"][0]["content"]["parts"][0]["text"]
    print(f"✅ It works!\n")
    print(f"Gemini says: {text}")
else:
    print(f"❌ Error! Status code: {response.status_code}")
    print(response.text)
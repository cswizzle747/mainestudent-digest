# summarize.py
# Collects events from all sources and sends them to AI
# for a fun weekly summary

import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from collect_all import collect_all_events

load_dotenv()


# ============================================================
# STEP 1: COLLECT ALL EVENTS
# ============================================================

print("\n🔍 Collecting events near Portland & Brunswick, ME...\n")

all_events = collect_all_events()

print(f"\n📊 Total events collected: {len(all_events)}")


# ============================================================
# STEP 2: BUILD THE EVENT LIST FOR THE AI
# ============================================================

events_text = ""
for event in all_events:
    events_text += f"Name: {event['name']}\n"
    if event.get("date"):
        events_text += f"Date: {event['date']} at {event.get('time', 'TBD')}\n"
    if event.get("venue"):
        events_text += f"Venue: {event['venue']}, {event.get('city', '')}\n"
    if event.get("category"):
        events_text += f"Type: {event['category']}\n"
    if event.get("price"):
        events_text += f"Price: {event['price']}\n"
    if event.get("url"):
        events_text += f"Link: {event['url']}\n"
    events_text += f"Source: {event['source']}\n"
    events_text += "---\n"


# ============================================================
# STEP 3: SEND TO AI FOR SUMMARIZATION
# ============================================================

print("\n🤖 Sending events to AI for summarization...\n")

groq_key = os.getenv("GROQ_API_KEY")

prompt = f"""You are writing a fun, engaging weekly events newsletter for 
college students in the Brunswick and Portland, Maine area. 

Here are the raw events happening in the next two weeks:

{events_text}

Please create an engaging weekly digest with these rules:

1. Write in a casual, fun tone — like a friend telling you what's going on
2. Group events into categories like:
   - 🎵 Live Music & Nightlife
   - 🏒 Sports
   - 🎭 Arts, Comedy & Theatre
   - 🏘️ Things to Do in Brunswick
   - 🎪 Community Events & Other Fun Stuff
3. For each event include the name, date, time, venue, and link
4. Add a brief, fun one-liner description or recommendation
5. If an event seems especially cool or noteworthy, hype it up
6. Skip any events that seem irrelevant, boring, or not aimed at college students
7. Remove obvious duplicates (same event different dates is fine to keep)
8. Start with a quick intro paragraph about what the week looks like
9. End with a "Don't Miss" section highlighting the top 3 events

Keep it concise but enthusiastic. This should be something people actually 
want to read, not a boring list."""

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {groq_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {
            "role": "system",
            "content": "You are a fun, knowledgeable local events writer for college students in Maine."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    "temperature": 0.7,
    "max_tokens": 4000
}

response = requests.post(url, headers=headers, json=data)

if response.status_code != 200:
    print(f"❌ AI error! Status code: {response.status_code}")
    print(response.text)
    exit()

result = response.json()
summary = result["choices"][0]["message"]["content"]


# ============================================================
# STEP 4: DISPLAY AND SAVE
# ============================================================

print("=" * 60)
print("📬 YOUR WEEKLY EVENTS DIGEST")
print("=" * 60)
print()
print(summary)
print()
print("=" * 60)

# Save it
summary_file = "weekly_digest_" + datetime.now().strftime("%Y-%m-%d") + ".txt"
with open(summary_file, "w") as f:
    f.write(summary)

print(f"\n💾 Summary saved to {summary_file}")
print("✅ Done!")

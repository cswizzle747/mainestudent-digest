# build_site.py
# Collects events, summarizes them, and builds a website

import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from collect_all import collect_all_events

load_dotenv()


# ============================================================
# STEP 1: COLLECT EVENTS
# ============================================================

print("\n🔍 Collecting events...\n")
all_events = collect_all_events()
print("\n📊 Total events collected: " + str(len(all_events)))


# ============================================================
# STEP 2: GET AI SUMMARY
# ============================================================

print("\n🤖 Generating summary...\n")

groq_key = os.getenv("GROQ_API_KEY")

events_text = ""
for event in all_events:
    events_text += "Name: " + event["name"] + "\n"
    if event.get("date"):
        events_text += "Date: " + event["date"] + " at " + event.get("time", "TBD") + "\n"
    if event.get("venue"):
        events_text += "Venue: " + event["venue"] + ", " + event.get("city", "") + "\n"
    if event.get("category"):
        events_text += "Type: " + event["category"] + "\n"
    if event.get("price"):
        events_text += "Price: " + event["price"] + "\n"
    if event.get("url"):
        events_text += "Link: " + event["url"] + "\n"
    events_text += "Source: " + event["source"] + "\n"
    events_text += "---\n"

prompt = """You are writing a fun, engaging weekly events newsletter for 
college students in the Brunswick and Portland, Maine area.

IMPORTANT: Output your response in HTML format. Use these HTML tags:
- <h2> for section headers
- <p> for paragraphs  
- <ul> and <li> for event lists
- <a href="URL" target="_blank"> for links
- <strong> for emphasis
- Use emojis in the section headers

Here are the raw events:

""" + events_text + """

Please create an engaging weekly digest with these rules:

1. Write in a casual, fun tone like a friend telling you whats going on
2. Group events into categories like:
   - 🎵 Live Music & Nightlife
   - 🏒 Sports
   - 🎭 Arts, Comedy & Theatre
   - 🏘️ Things to Do in Brunswick
   - 🎪 Community Events & Other Fun Stuff
3. For each event include the name, date, time, venue, and a clickable link
4. Add a brief fun one-liner description
5. If an event seems especially cool hype it up
6. Skip irrelevant or non-college-student events
7. Start with a quick intro paragraph
8. End with a Dont Miss top 3 section

Output ONLY the HTML content. No markdown. No code fences."""

api_url = "https://api.groq.com/openai/v1/chat/completions"

api_headers = {
    "Authorization": "Bearer " + groq_key,
    "Content-Type": "application/json"
}

api_data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {
            "role": "system",
            "content": "You are a fun local events writer. Output HTML only."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    "temperature": 0.7,
    "max_tokens": 4000
}

response = requests.post(api_url, headers=api_headers, json=api_data)

if response.status_code != 200:
    print("❌ AI error! Status code: " + str(response.status_code))
    print(response.text)
    exit()

result = response.json()
summary_html = result["choices"][0]["message"]["content"]


# ============================================================
# STEP 3: BUILD THE HTML PAGE
# ============================================================

today = datetime.now().strftime("%B %d, %Y")

html_page = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whats Happening | Portland and Brunswick, ME</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .content {
            max-width: 800px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .digest {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .digest h2 {
            color: #667eea;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 8px;
        }
        .digest h2:first-child {
            margin-top: 0;
        }
        .digest p {
            margin-bottom: 15px;
        }
        .digest ul {
            list-style: none;
            padding: 0;
        }
        .digest li {
            padding: 12px 15px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .digest a {
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }
        .digest a:hover {
            text-decoration: underline;
        }
        .digest strong {
            color: #333;
        }
        .footer {
            text-align: center;
            padding: 30px;
            color: #999;
            font-size: 0.9em;
        }
        .updated {
            background: #e8f4f8;
            padding: 10px 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Whats Happening</h1>
        <p>Portland and Brunswick, Maine — Weekly Events Digest</p>
    </div>
    <div class="content">
        <div class="updated">
            Last updated: """ + today + """
        </div>
        <div class="digest">
            """ + summary_html + """
        </div>
    </div>
    <div class="footer">
        <p>Built with Python, Groq AI, and coffee</p>
        <p>Data from Ticketmaster, Eventbrite, and Brunswick Downtown Association</p>
    </div>
</body>
</html>"""


# ============================================================
# STEP 4: SAVE THE HTML FILE
# ============================================================

os.makedirs("docs", exist_ok=True)

with open("docs/index.html", "w") as f:
    f.write(html_page)

print("✅ Website built!")
print("💾 Saved to docs/index.html")
print("📂 Open it in your browser to preview:")
print("   open docs/index.html")
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# --- TEST TICKETMASTER ---
print("Testing Ticketmaster...")
tm_key = os.getenv("TICKETMASTER_API_KEY")

tm_response = requests.get(
    "https://app.ticketmaster.com/discovery/v2/events.json",
    params={"apikey": tm_key, "size": "1"}
)

if tm_response.status_code == 200:
    print("✅ Ticketmaster key works!\n")
elif tm_response.status_code == 401:
    print("❌ Ticketmaster key not authorized — might need approval\n")
else:
    print(f"⚠️  Ticketmaster returned status code: {tm_response.status_code}\n")


# --- TEST EVENTBRITE ---
print("Testing Eventbrite...")
eb_key = os.getenv("EVENTBRITE_API_KEY")

eb_response = requests.get(
    "https://www.eventbriteapi.com/v3/users/me/",
    headers={"Authorization": f"Bearer {eb_key}"}
)

if eb_response.status_code == 200:
    print("✅ Eventbrite key works!\n")
elif eb_response.status_code == 401:
    print("❌ Eventbrite key not authorized — might need approval\n")
else:
    print(f"⚠️  Eventbrite returned status code: {eb_response.status_code}\n")
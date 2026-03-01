# ticketmaster.py
# Pulls events from Ticketmaster near Portland/Brunswick, ME

import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# --- SETTINGS ---

LATITUDE = "43.6591"
LONGITUDE = "-70.2568"
RADIUS_MILES = "35"
DAYS_AHEAD = 14

SKIP_WORDS = [
    "parking", "vip upgrade", "upsell",
    "meet & greet", "premium experience",
]


# --- MAIN FUNCTION ---

def get_events():
    print("📡 Fetching from Ticketmaster...")
    api_key = os.getenv("TICKETMASTER_API_KEY")
    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    today = datetime.now().strftime("%Y-%m-%dT00:00:00Z")
    end_date = (datetime.now() + timedelta(days=DAYS_AHEAD)).strftime("%Y-%m-%dT23:59:59Z")

    params = {
        "apikey": api_key,
        "latlong": f"{LATITUDE},{LONGITUDE}",
        "radius": RADIUS_MILES,
        "unit": "miles",
        "size": "50",
        "sort": "date,asc",
        "startDateTime": today,
        "endDateTime": end_date,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"   ❌ Ticketmaster error: {response.status_code}")
        return []

    data = response.json()
    if "_embedded" not in data:
        print("   ⚠️  No Ticketmaster events found")
        return []

    events = []
    seen = set()

    for event in data["_embedded"]["events"]:
        name = event.get("name", "Unknown")
        name_lower = name.lower()

        if any(word in name_lower for word in SKIP_WORDS):
            continue

        dates = event.get("dates", {}).get("start", {})
        date = dates.get("localDate", "Unknown")
        time = dates.get("localTime", "Unknown")

        unique_key = f"{name_lower}_{date}"
        if unique_key in seen:
            continue
        seen.add(unique_key)

        venues = event.get("_embedded", {}).get("venues", [])
        if venues:
            venue_name = venues[0].get("name", "Unknown venue")
            venue_city = venues[0].get("city", {}).get("name", "")
        else:
            venue_name = "Unknown venue"
            venue_city = ""

        event_type = ""
        classifications = event.get("classifications", [])
        if classifications:
            segment = classifications[0].get("segment", {}).get("name", "")
            genre = classifications[0].get("genre", {}).get("name", "")
            event_type = f"{segment} — {genre}"

        price_info = "See link"
        price_ranges = event.get("priceRanges", [])
        if price_ranges:
            low = price_ranges[0].get("min", "")
            high = price_ranges[0].get("max", "")
            if low and high:
                price_info = f"${low:.0f} - ${high:.0f}"

        events.append({
            "name": name,
            "date": date,
            "time": time,
            "venue": venue_name,
            "city": venue_city,
            "category": event_type,
            "price": price_info,
            "url": event.get("url", ""),
            "source": "Ticketmaster"
        })

    print(f"   ✅ Got {len(events)} events from Ticketmaster")
    return events


# This only runs if you run this file directly
if __name__ == "__main__":
    events = get_events()
    for event in events:
        print(f"🎫 {event['name']} — {event['date']}")
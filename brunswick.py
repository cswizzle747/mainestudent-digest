# brunswick.py
# Pulls events from Brunswick Downtown Association website

import requests
import json
from bs4 import BeautifulSoup

# --- SETTINGS ---

URL = "https://brunswickdowntown.org/all-events/"


# --- MAIN FUNCTION ---

def get_events():
    print("📡 Fetching from Brunswick Downtown...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Brunswick Downtown error: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    events_found = []

    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if item.get("@type") == "Event":
                        events_found.append(item)
            elif isinstance(data, dict):
                if data.get("@type") == "Event":
                    events_found.append(data)
        except (json.JSONDecodeError, TypeError):
            continue

    events = []
    seen = set()

    for event in events_found:
        name = event.get("name", "No name")
        if name in seen:
            continue
        seen.add(name)
        name = name.replace("&amp;", "&")

        start_date = event.get("startDate", "")
        end_date = event.get("endDate", "")

        if "T" in str(start_date):
            date = start_date.split("T")[0]
            time_start = start_date.split("T")[1][:5]
        else:
            date = start_date
            time_start = ""

        if "T" in str(end_date):
            time_end = end_date.split("T")[1][:5]
        else:
            time_end = ""

        if time_start and time_end:
            time_display = time_start + " - " + time_end
        elif time_start:
            time_display = time_start
        else:
            time_display = ""

        location = event.get("location", {})
        if isinstance(location, dict):
            venue = location.get("name", "")
            venue = venue.replace("&amp;", "&")
            address = location.get("address", {})
            city = address.get("addressLocality", "Brunswick") if isinstance(address, dict) else "Brunswick"
        else:
            venue = ""
            city = "Brunswick"

        description = event.get("description", "")

        events.append({
            "name": name, "date": date, "time": time_display,
            "venue": venue, "city": city,
            "category": "", "price": "",
            "description": description,
            "url": event.get("url", ""), "source": "Brunswick Downtown"
        })

    print(f"   ✅ Got {len(events)} events from Brunswick Downtown")
    return events


if __name__ == "__main__":
    events = get_events()
    for event in events:
        print(f"🏘️  {event['name']} — {event['date']}")
# eventbrite.py
# Scrapes events from Eventbrite website near Portland, ME

import requests
import json
from bs4 import BeautifulSoup

# --- SETTINGS ---

SEARCH_URL = "https://www.eventbrite.com/d/me--portland/events/"

SKIP_WORDS = [
    "career fair", "hiring event", "industry",
    "business leaders", "professional development",
    "conference", "webinar", "certification",
    "training course", "continuing education",
    "board meeting", "shareholder", "compliance",
    "workplace safety", "osha", "computational",
    "modelling", "spark series", "power hour",
    "lecture", "reform", "q&a",
    "speed dating", "wedding", "40-50", "50-60",
    "retirement", "senior", "real estate",
    "housing market", "designing housing",
    "patrons of the", "eventbrite.ca",
    "eventbrite.co.uk", "eventbrite.de",
]

KEEP_WORDS = [
    "music", "concert", "live", "dj", "band", "open mic",
    "night", "karaoke", "food", "dinner", "brunch", "tasting",
    "beer", "wine", "cocktail", "brewery", "art", "gallery",
    "theater", "theatre", "comedy", "film", "movie",
    "book fair", "poetry", "museum", "festival", "market",
    "trivia", "scavenger", "party", "fair", "craft",
    "dance", "celebration", "hike", "kayak", "sailing",
    "outdoor", "run", "yoga", "beach", "bike",
    "portland", "brunswick", "freeport", "maine",
]


# --- MAIN FUNCTION ---

def get_events():
    print("📡 Fetching from Eventbrite...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(SEARCH_URL, headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Eventbrite error: {response.status_code}")
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

    if not events_found:
        event_links = soup.find_all("a", href=True)
        for link in event_links:
            href = link.get("href", "")
            if "/e/" in href and "tickets-" in href:
                title = link.get_text(strip=True)
                if title and len(title) > 5:
                    events_found.append({
                        "name": title,
                        "url": href if href.startswith("http") else f"https://www.eventbrite.com{href}",
                        "raw": True
                    })

    events = []
    seen = set()

    for event in events_found:
        name = event.get("name", "")
        if isinstance(name, dict):
            name = name.get("text", str(name))
        if not name:
            continue

        name_lower = name.lower()
        if name in seen:
            continue

        event_url = event.get("url", "")
        combined_text = name_lower + " " + event_url.lower()

        if any(word in combined_text for word in SKIP_WORDS):
            continue
        if not any(word in combined_text for word in KEEP_WORDS):
            continue

        seen.add(name)

        if not event.get("raw"):
            start_date = event.get("startDate", "")
            location = event.get("location", {})
            if isinstance(location, dict):
                venue_name = location.get("name", "Unknown venue")
                address = location.get("address", {})
                city = address.get("addressLocality", "") if isinstance(address, dict) else ""
            else:
                venue_name = "Unknown venue"
                city = ""

            if "T" in str(start_date):
                date = start_date.split("T")[0]
                time = start_date.split("T")[1][:5]
            else:
                date = start_date
                time = ""

            events.append({
                "name": name, "date": date, "time": time,
                "venue": venue_name, "city": city,
                "category": "", "price": "",
                "url": event.get("url", ""), "source": "Eventbrite"
            })
        else:
            events.append({
                "name": name, "date": "", "time": "",
                "venue": "", "city": "",
                "category": "", "price": "",
                "url": event.get("url", ""), "source": "Eventbrite"
            })

    print(f"   ✅ Got {len(events)} events from Eventbrite")
    return events


if __name__ == "__main__":
    events = get_events()
    for event in events:
        print(f"🎪 {event['name']} — {event['date']}")
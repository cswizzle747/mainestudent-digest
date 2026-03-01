# eventbrite.py
# Scrapes events from Eventbrite website near Portland, ME
# Now visits each event page to get venue info!

import requests
import json
import time
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


# --- HELPER: GET VENUE FROM INDIVIDUAL EVENT PAGE ---

def get_venue_from_event_page(event_url):
    try:
        time.sleep(1)  # be polite, don't hammer their server
        response = requests.get(event_url, headers=HEADERS)
        if response.status_code != 200:
            return "", ""

        soup = BeautifulSoup(response.text, "html.parser")

        # Check structured data on the event page
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)

                # Sometimes it's nested in a list
                if isinstance(data, list):
                    for item in data:
                        if item.get("@type") == "Event":
                            data = item
                            break

                if isinstance(data, dict) and data.get("@type") == "Event":
                    location = data.get("location", {})
                    if isinstance(location, dict):
                        venue = location.get("name", "")
                        address = location.get("address", {})
                        if isinstance(address, dict):
                            city = address.get("addressLocality", "")
                        else:
                            city = ""
                        if venue:
                            return venue, city
            except (json.JSONDecodeError, TypeError):
                continue

        # Fallback: look for location in meta tags
        meta_location = soup.find("meta", {"property": "event:location:name"})
        if meta_location:
            return meta_location.get("content", ""), ""

        # If we still can't find it, return empty (not unknown)
        return "", ""

    except Exception:
        return "", ""


# --- MAIN FUNCTION ---

def get_events():
    print("📡 Fetching from Eventbrite...")

    response = requests.get(SEARCH_URL, headers=HEADERS)
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
                        "url": href if href.startswith("http") else "https://www.eventbrite.com" + href,
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

        # Get date from search page data
        if not event.get("raw"):
            start_date = event.get("startDate", "")
            if "T" in str(start_date):
                date = start_date.split("T")[0]
                time_val = start_date.split("T")[1][:5]
            else:
                date = start_date
                time_val = ""
        else:
            date = ""
            time_val = ""

        # Now visit the individual event page to get the venue
        print(f"   🔍 Getting venue for: {name[:50]}...")
        venue_name, venue_city = get_venue_from_event_page(event_url)

        events.append({
            "name": name,
            "date": date,
            "time": time_val,
            "venue": venue_name if venue_name and "autocomplete" not in venue_name else "See link for details",
            "city": venue_city,
            "category": "",
            "price": "",
            "url": event_url,
            "source": "Eventbrite"
        })

    print(f"   ✅ Got {len(events)} events from Eventbrite")
    return events


if __name__ == "__main__":
    events = get_events()
    for event in events:
        print(f"🎪 {event['name']}")
        print(f"   📍 {event['venue']}, {event['city']}")
        print(f"   📅 {event['date']}")
        print()
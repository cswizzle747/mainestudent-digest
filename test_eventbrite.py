# test_eventbrite.py
# Let's see what data Eventbrite actually gives us

import requests
import json
from bs4 import BeautifulSoup

url = "https://www.eventbrite.com/d/me--portland/events/"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

print("Fetching Eventbrite page...")
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, "html.parser")

# Check structured data
scripts = soup.find_all("script", type="application/ld+json")
print(f"Found {len(scripts)} JSON-LD blocks\n")

for i, script in enumerate(scripts):
    try:
        data = json.loads(script.string)

        if isinstance(data, list):
            for item in data:
                if item.get("@type") == "Event":
                    print("=" * 60)
                    print("NAME: " + str(item.get("name", "no name")))
                    print("DATE: " + str(item.get("startDate", "no date")))
                    print("LOCATION: " + json.dumps(item.get("location", "none"), indent=2))
                    print("URL: " + str(item.get("url", "no url")))
                    print()

        elif isinstance(data, dict):
            if data.get("@type") == "Event":
                print("=" * 60)
                print("NAME: " + str(data.get("name", "no name")))
                print("DATE: " + str(data.get("startDate", "no date")))
                print("LOCATION: " + json.dumps(data.get("location", "none"), indent=2))
                print("URL: " + str(data.get("url", "no url")))
                print()

    except (json.JSONDecodeError, TypeError):
        continue

# Also check if there's a different way to find venue info
print("\n" + "=" * 60)
print("CHECKING FOR VENUE INFO IN OTHER PLACES")
print("=" * 60)

# Look for location-related elements
location_elements = soup.find_all(class_=lambda x: x and "location" in x.lower())
print(f"\nFound {len(location_elements)} elements with 'location' in class")
for el in location_elements[:5]:
    print(f"  Class: {el.get('class')}")
    print(f"  Text: {el.get_text(strip=True)[:100]}")
    print()

venue_elements = soup.find_all(class_=lambda x: x and "venue" in x.lower())
print(f"Found {len(venue_elements)} elements with 'venue' in class")
for el in venue_elements[:5]:
    print(f"  Class: {el.get('class')}")
    print(f"  Text: {el.get_text(strip=True)[:100]}")
    print()
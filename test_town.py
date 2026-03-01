# test_town.py
# Let's see what the Brunswick Downtown events page looks like

import requests
from bs4 import BeautifulSoup

url = "https://brunswickdowntown.org/all-events/"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

print("Fetching Brunswick Downtown events page...")
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"Error! Status code: {response.status_code}")
    exit()

print(f"Success! Page is {len(response.text)} characters long.\n")

soup = BeautifulSoup(response.text, "html.parser")

# --- TEST 1: Look for common event patterns ---

print("=" * 60)
print("TEST 1: Looking for elements with 'event' in the class name")
print("=" * 60)

event_elements = soup.find_all(class_=lambda x: x and "event" in x.lower())
print(f"Found {len(event_elements)} elements\n")

for i, el in enumerate(event_elements[:5]):  # just show first 5
    print(f"--- Element {i+1} ---")
    print(f"Tag: <{el.name}>")
    print(f"Class: {el.get('class')}")
    print(f"Text preview: {el.get_text(strip=True)[:100]}")
    print()

# --- TEST 2: Look for headings that might be event titles ---

print("=" * 60)
print("TEST 2: Looking for h2 and h3 headings")
print("=" * 60)

headings = soup.find_all(["h2", "h3"])
print(f"Found {len(headings)} headings\n")

for i, h in enumerate(headings[:10]):  # show first 10
    text = h.get_text(strip=True)
    link = h.find("a")
    href = link.get("href", "") if link else "no link"
    print(f"  {i+1}. {text}")
    print(f"     Link: {href}")
    print()

# --- TEST 3: Look for structured data ---

print("=" * 60)
print("TEST 3: Looking for structured data (JSON-LD)")
print("=" * 60)

scripts = soup.find_all("script", type="application/ld+json")
print(f"Found {len(scripts)} JSON-LD blocks\n")

import json
for i, script in enumerate(scripts):
    try:
        data = json.loads(script.string)
        print(f"Block {i+1}:")
        print(json.dumps(data, indent=2)[:500])
        print()
    except:
        print(f"Block {i+1}: couldn't parse")

# --- TEST 4: Look for time/date elements ---

print("=" * 60)
print("TEST 4: Looking for time and date elements")
print("=" * 60)

time_elements = soup.find_all("time")
print(f"Found {len(time_elements)} <time> elements\n")

for t in time_elements[:5]:
    print(f"  datetime: {t.get('datetime', 'none')}")
    print(f"  text: {t.get_text(strip=True)}")
    print()

# --- TEST 5: Save the raw HTML so we can look at it ---

with open("brunswick_raw.html", "w") as f:
    f.write(response.text)

print("=" * 60)
print("Saved full HTML to brunswick_raw.html")
print("You can open this file in VS Code to look at it")
print("=" * 60)
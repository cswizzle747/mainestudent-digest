# collect_all.py
# Imports all sources and combines them
# To add a new source, just create a new file with a get_events() function
# and add it to the SOURCES list below!

import json
from datetime import datetime

# Import each source
import ticketmaster
import eventbrite
import brunswick

# --- ADD YOUR SOURCES HERE ---
# Just add new ones to this list!

SOURCES = [
    ticketmaster,
    eventbrite,
    brunswick,
]


# --- COLLECT FROM ALL SOURCES ---

def collect_all_events():
    all_events = []

    for source in SOURCES:
        events = source.get_events()
        all_events.extend(events)

    # Sort by date
    all_events.sort(key=lambda x: x.get("date", "9999-99-99"))
    return all_events


# --- ONLY RUNS IF YOU RUN THIS FILE DIRECTLY ---

if __name__ == "__main__":
    print("\n🔍 Collecting events near Portland & Brunswick, ME...\n")

    all_events = collect_all_events()

    print(f"\n📊 Total events collected: {len(all_events)}\n")
    print("=" * 60)

    for event in all_events:
        name = event.get("name", "No name")
        date = event.get("date", "")
        time = event.get("time", "")
        venue = event.get("venue", "")
        city = event.get("city", "")
        category = event.get("category", "")
        price = event.get("price", "")
        source = event.get("source", "")
        url = event.get("url", "")

        print(f"🎯 {name}")
        if date:
            print(f"   📅 {date} at {time}")
        if venue:
            print(f"   📍 {venue}, {city}")
        if category:
            print(f"   🏷️  {category}")
        if price:
            print(f"   💰 {price}")
        print(f"   📌 Source: {source}")
        print(f"   🔗 {url}")
        print("-" * 60)

    # Save to file
    filename = "events_" + datetime.now().strftime("%Y-%m-%d") + ".json"
    with open(filename, "w") as f:
        json.dump(all_events, f, indent=2)

    print("\n💾 Saved all events to " + filename)
    print("📊 Total: " + str(len(all_events)) + " events from " + str(len(SOURCES)) + " sources")
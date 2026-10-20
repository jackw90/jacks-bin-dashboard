import os
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UPRN = os.environ["JACK_UPRN"]

API_URL = (
    "https://ukbinday.co.uk/api/v2/"
    f"E07000068/view/{UPRN}"
)

OUTPUT = Path("bins.json")

def fetch_bins():
    request = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "ESP32-Bin-Display/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)

    if not isinstance(data.get("dates"), list):
        raise ValueError("API response has no dates list")

    collections = []

    for item in data["dates"]:
        collections.append({
            "date": item["date"],
            "type": item["type"]["label"],
            "colour": item["type"].get("colour")
        })

    collections.sort(key=lambda x: (x["date"], x["type"]))

    result = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "collections": collections
    }

    OUTPUT.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8"
    )

    print(f"Saved {len(collections)} collections to {OUTPUT}")

if __name__ == "__main__":
    fetch_bins()

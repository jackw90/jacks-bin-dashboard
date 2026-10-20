
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Brentwood Borough Council
COUNCIL = "E07000068"
API_BASE = f"https://ukbinday.co.uk/api/v2/{COUNCIL}/view"

# Property names and corresponding GitHub secrets
PROPERTIES = {
    "jack": "JACK_UPRN",
    "mark": "MARK_UPRN",
    "clare": "CLARE_UPRN",
}


def fetch_property(name, secret_name):
    uprn = os.environ[secret_name]

    url = f"{API_BASE}/{uprn}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Jacks-Bin-Dashboard/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)

    if not isinstance(data.get("dates"), list):
        raise ValueError(f"No collection dates returned for {name}")

    collections = [
        {
            "date": item["date"],
            "type": item["type"]["label"],
            "colour": item["type"].get("colour"),
        }
        for item in data["dates"]
    ]

    collections.sort(key=lambda x: (x["date"], x["type"]))

    return {
        "updated": datetime.now(timezone.utc).isoformat(),
        "collections": collections,
    }


def main():
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    for name, secret_name in PROPERTIES.items():
        result = fetch_property(name, secret_name)

        output = output_dir / f"{name}.json"
        output.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8"
        )

        print(
            f"Saved {len(result['collections'])} "
            f"collections to {output}"
        )

    # Keep the existing dashboard working using Jack's collections
    jack_data = (output_dir / "jack.json").read_text(
        encoding="utf-8"
    )

    Path("bins.json").write_text(
        jack_data,
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()

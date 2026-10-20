
import json
import os
import urllib.request
from urllib.parse import urlencode
from urllib.error import HTTPError
from datetime import datetime, timezone
from pathlib import Path

PROPERTIES = {
    "jack": {
        "council": "E07000068",
        "secret": "JACK_UPRN",
    },
    "mark": {
        "council": "E07000067",
        "secret": "MARK_UPRN",
    },
    "clare": {
        "council": "E07000070",
        "secret": "CLARE_UPRN",
    },
}


def fetch_property(name, config):
    uprn = os.environ[config["secret"]]
    council = config["council"]

    url = f"https://ukbinday.co.uk/api/v2/{council}/view/{uprn}"

    if name == "mark":
        params = {
            "postcode": os.environ["MARK_POSTCODE"],
            "house_number": os.environ["MARK_HOUSE_NUMBER"],
            "street": os.environ["MARK_STREET"],
            "address": os.environ["MARK_ADDRESS"],
        }
        url += "?" + urlencode(params)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Jacks-Bin-Dashboard/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
    except HTTPError as error:
        raise RuntimeError(
            f"Bin collection lookup failed for {name} "
            f"(HTTP {error.code})"
        ) from None

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

    for name, config in PROPERTIES.items():
        result = fetch_property(name, config)

        output = output_dir / f"{name}.json"
        output.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
        )

        print(f"Saved {len(result['collections'])} collections for {name}")

    # Keep Jack's original dashboard working
    Path("bins.json").write_text(
        (output_dir / "jack.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

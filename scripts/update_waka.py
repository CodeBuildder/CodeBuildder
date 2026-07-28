import base64
import json
import os
import re
import urllib.request
from pathlib import Path

WIDTH = 12
LIMIT = 4
IGNORED = {"CSS", "Other", "JSON", "Text", "Markdown", "Git Config", "Image (svg)"}


def activity_bar(percent: float) -> str:
    units = percent / 100 * WIDTH
    full = int(units)
    fraction = units - full
    partial = "▓" if fraction >= 0.66 else "▒" if fraction >= 0.2 else ""
    return ("█" * full + partial).ljust(WIDTH, "░")[:WIDTH]


key = os.environ["WAKATIME_API_KEY"]
request = urllib.request.Request("https://wakatime.com/api/v1/users/current/stats/last_7_days")
token = base64.b64encode(f"{key}:".encode()).decode()
request.add_header("Authorization", f"Basic {token}")

with urllib.request.urlopen(request) as response:
    stats = json.load(response)["data"]

languages = [item for item in stats["languages"] if item["name"] not in IGNORED][:LIMIT]
lines = [
    f'{item["name"]:<12} {item["text"]:<15} {activity_bar(item["percent"])}   {item["percent"]:05.2f} %'
    for item in languages
]
replacement = "<!--START_SECTION:waka-->\n\n```txt\n" + "\n".join(lines) + "\n```\n\n<!--END_SECTION:waka-->"

readme = Path("README.md")
content = readme.read_text()
updated = re.sub(
    r"<!--START_SECTION:waka-->.*?<!--END_SECTION:waka-->",
    replacement,
    content,
    flags=re.DOTALL,
)
readme.write_text(updated)

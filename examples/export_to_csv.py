"""
Scrape TikTok profiles and export the flattened results to CSV.

Drop into Excel, Google Sheets, Numbers, or import into a database.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/export_to_csv.py > profiles.csv
"""

import csv
import sys

from tiktok_profile_scraper import TikTokProfileClient


USERNAMES = [
    "khaby.lame",
    "charlidamelio",
    "addisonre",
    "bellapoarch",
    "thejugglingjosh",
    "willsmith",
]


COLUMNS = [
    "username",
    "uniqueId",
    "nickname",
    "id",
    "secUid",
    "verified",
    "privateAccount",
    "signature",
    "avatar",
    "profile_url",
    "followers",
    "following",
    "likes",
    "videos",
    "friends",
    "creator_tier",
    "influence_score",
    "engagement_rate_pct",
    "avg_likes_per_video",
    "likes_per_follower",
]


def flatten(rec: dict) -> dict:
    if "stats" not in rec:
        return {"username": rec.get("username"), "error": rec.get("error", "?")}
    stats = rec.get("stats") or {}
    out = {}
    for col in COLUMNS:
        if col in ("followers", "following", "likes", "videos", "friends"):
            out[col] = stats.get(col)
        else:
            out[col] = rec.get(col)
    return out


def main() -> None:
    client = TikTokProfileClient()
    profiles = client.scrape(USERNAMES)

    writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
    writer.writeheader()
    for r in profiles:
        if "stats" not in r:
            continue
        writer.writerow(flatten(r))


if __name__ == "__main__":
    main()

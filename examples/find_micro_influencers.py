"""
Filter a candidate list down to micro-influencers worth pitching.

Definition used here:
    creator_tier == "micro" or "nano"  (10k-500k followers)
    AND engagement_rate_pct >= 3       (healthy, not bot-driven)
    AND verified or videos >= 30       (active, brand-safe)

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/find_micro_influencers.py
"""

from tiktok_profile_scraper import TikTokProfileClient


CANDIDATES = [
    "thejugglingjosh",
    "khaby.lame",
    "addisonre",
    "tiktok",
    "willsmith",
    "lizzo",
    "bellapoarch",
    "charlidamelio",
]


def main() -> None:
    client = TikTokProfileClient()
    profiles = client.scrape(CANDIDATES)

    shortlist = []
    for p in profiles:
        if "stats" not in p:
            continue
        tier = p.get("creator_tier")
        engagement = p.get("engagement_rate_pct") or 0
        videos = p.get("stats", {}).get("videos") or 0
        verified = p.get("verified", False)

        if tier in ("nano", "micro") and engagement >= 3 and (verified or videos >= 30):
            shortlist.append(p)

    verified_mark = "\u2713 verified"
    print(f"\nFound {len(shortlist)} micro-influencer candidates:")
    for p in sorted(shortlist, key=lambda x: -(x.get("influence_score") or 0)):
        flag = verified_mark if p["verified"] else ""
        print(
            f"  @{p['username']:<20} "
            f"{p['stats']['followers']:>9,} followers  "
            f"{p['engagement_rate_pct']:>5.1f}% eng  "
            f"tier={p['creator_tier']}  "
            f"{flag}"
        )


if __name__ == "__main__":
    main()

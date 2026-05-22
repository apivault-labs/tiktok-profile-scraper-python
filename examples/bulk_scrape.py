"""
Scrape many TikTok profiles in one batch.

The actor itself fetches them with retries on Apify infrastructure, so a
single ``scrape`` call with many usernames is faster and cheaper than
calling the SDK once per username.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/bulk_scrape.py
"""

from tiktok_profile_scraper import TikTokProfileClient


USERNAMES = [
    "khaby.lame",
    "charlidamelio",
    "addisonre",
    "bellapoarch",
    "willsmith",
    "thejugglingjosh",
    "lizzo",
    "tiktok",
]


def main() -> None:
    client = TikTokProfileClient(timeout=900)
    print(f"Scraping {len(USERNAMES)} profiles "
          f"(estimated cost: ${client.estimate_cost(len(USERNAMES))})...\n")

    profiles = client.scrape(USERNAMES, max_retries=3)

    print(f"{'Username':<22} {'Tier':<8} {'Followers':>14} "
          f"{'Engagement':>11} {'Influence':>9}")
    print("-" * 72)
    for p in sorted(
        profiles,
        key=lambda x: -(x.get("influence_score") or 0),
    ):
        if "error" in p and "stats" not in p:
            print(f"  ERROR: @{p.get('username')}: {p.get('error', '?')[:50]}")
            continue
        username = (p.get("username") or "?")[:22]
        tier = (p.get("creator_tier") or "?")[:8]
        followers = p.get("stats", {}).get("followers") or 0
        engagement = p.get("engagement_rate_pct") or 0
        influence = p.get("influence_score") or 0
        print(f"{username:<22} {tier:<8} {followers:>14,} "
              f"{engagement:>10.1f}% {influence:>9}")


if __name__ == "__main__":
    main()

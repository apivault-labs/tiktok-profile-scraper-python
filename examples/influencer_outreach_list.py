"""
Build a ranked outreach list for influencer partnerships.

Combines `creator_tier`, engagement, and verification into a single sort
key, then filters out anyone too small or with suspicious metrics.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/influencer_outreach_list.py
"""

from tiktok_profile_scraper import TikTokProfileClient


CANDIDATES = [
    "khaby.lame",
    "addisonre",
    "thejugglingjosh",
    "charlidamelio",
    "bellapoarch",
    "willsmith",
    "lizzo",
    "tiktok",
]


# Tunable thresholds
MIN_FOLLOWERS = 5_000
MIN_VIDEOS = 5
MIN_ENGAGEMENT_PCT = 1.0


def outreach_score(p: dict) -> float:
    """Composite score: influence × engagement, with a verified bonus."""
    base = (p.get("influence_score") or 0)
    eng = (p.get("engagement_rate_pct") or 0)
    bonus = 10 if p.get("verified") else 0
    return base + (eng * 0.5) + bonus


def main() -> None:
    client = TikTokProfileClient()
    profiles = client.scrape(CANDIDATES)

    candidates = []
    for p in profiles:
        if "stats" not in p:
            continue
        if p["stats"]["followers"] < MIN_FOLLOWERS:
            continue
        if p["stats"]["videos"] < MIN_VIDEOS:
            continue
        if (p.get("engagement_rate_pct") or 0) < MIN_ENGAGEMENT_PCT:
            continue
        if p.get("privateAccount"):
            continue
        candidates.append(p)

    candidates.sort(key=outreach_score, reverse=True)

    print(f"\nTop {len(candidates)} outreach candidates:\n")
    print(f"{'#':<3} {'Handle':<22} {'Tier':<7} {'Followers':>11} "
          f"{'Eng %':>7} {'Score':>6}")
    print("-" * 64)
    for i, p in enumerate(candidates, start=1):
        print(
            f"{i:<3} "
            f"@{p['username']:<21} "
            f"{p['creator_tier']:<7} "
            f"{p['stats']['followers']:>11,} "
            f"{p['engagement_rate_pct']:>6.1f}% "
            f"{outreach_score(p):>6.1f}"
        )


if __name__ == "__main__":
    main()

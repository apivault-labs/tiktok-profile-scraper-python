"""
Keep only verified TikTok accounts from a candidate list.

Use case: brand-safety vetting before signing UGC partnerships, or quickly
splitting a large candidate list into "blue checkmark" vs "regular".

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/verified_only.py
"""

from tiktok_profile_scraper import TikTokProfileClient


CANDIDATES = [
    "khaby.lame",
    "thejugglingjosh",
    "addisonre",
    "bellapoarch",
    "tiktok",
    "lizzo",
]


def main() -> None:
    client = TikTokProfileClient()
    profiles = client.scrape(CANDIDATES)

    verified = [p for p in profiles if p.get("verified")]
    unverified = [p for p in profiles if "stats" in p and not p.get("verified")]
    failed = [p for p in profiles if "stats" not in p]

    print(f"\n\u2713  Verified ({len(verified)}):")
    for p in verified:
        print(f"   @{p['username']} — {p['stats']['followers']:,} followers")

    print(f"\n\u00b7  Unverified ({len(unverified)}):")
    for p in unverified:
        print(f"   @{p['username']} — {p['stats']['followers']:,} followers")

    if failed:
        print(f"\n\u2715  Failed to scrape ({len(failed)}):")
        for p in failed:
            print(f"   @{p.get('username')} — {p.get('error', '?')[:80]}")


if __name__ == "__main__":
    main()

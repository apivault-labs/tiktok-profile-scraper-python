"""
Quickstart: scrape a single TikTok profile.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/quickstart.py
"""

from tiktok_profile_scraper import TikTokProfileClient


def main() -> None:
    client = TikTokProfileClient()  # picks up APIFY_API_TOKEN from env

    profile = client.scrape_one("khaby.lame")

    print(f"\n=== {profile.get('nickname')} (@{profile.get('username')}) ===")
    print(f"  Verified:           {profile.get('verified')}")
    print(f"  Private:            {profile.get('privateAccount')}")
    print(f"  Followers:          {profile['stats']['followers']:,}")
    print(f"  Following:          {profile['stats']['following']:,}")
    print(f"  Total likes:        {profile['stats']['likes']:,}")
    print(f"  Videos:             {profile['stats']['videos']:,}")
    print()
    print(f"  Creator tier:       {profile.get('creator_tier')}")
    print(f"  Influence score:    {profile.get('influence_score')}/100")
    print(f"  Engagement rate:    {profile.get('engagement_rate_pct')}%")
    print(f"  Avg likes/video:    {profile.get('avg_likes_per_video'):,.0f}")
    print()
    print(f"  Bio: {profile.get('signature')}")
    print(f"  Profile URL: {profile.get('profile_url')}")


if __name__ == "__main__":
    main()

"""
Compare two TikTok creators side-by-side.

Use case: which competitor has higher per-follower engagement, fewer
videos but more virality, or a stronger niche signal in the bio?

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/competitor_overlap.py
"""

from tiktok_profile_scraper import TikTokProfileClient


CREATOR_A = "khaby.lame"
CREATOR_B = "charlidamelio"


def main() -> None:
    client = TikTokProfileClient()
    a, b = client.scrape([CREATOR_A, CREATOR_B])

    if "stats" not in a or "stats" not in b:
        print("One or both profiles failed to scrape.")
        return

    rows = [
        ("Followers",          a["stats"]["followers"],     b["stats"]["followers"]),
        ("Following",          a["stats"]["following"],     b["stats"]["following"]),
        ("Total likes",        a["stats"]["likes"],         b["stats"]["likes"]),
        ("Videos",             a["stats"]["videos"],        b["stats"]["videos"]),
        ("Avg likes/video",    a["avg_likes_per_video"],    b["avg_likes_per_video"]),
        ("Engagement rate %",  a["engagement_rate_pct"],    b["engagement_rate_pct"]),
        ("Influence score",    a["influence_score"],        b["influence_score"]),
        ("Creator tier",       a["creator_tier"],           b["creator_tier"]),
        ("Verified",           a["verified"],               b["verified"]),
    ]

    print(f"\n{'Metric':<22} {'@'+CREATOR_A:<22} {'@'+CREATOR_B:<22} {'Winner':<8}")
    print("-" * 76)
    for label, va, vb in rows:
        try:
            winner = "A" if (vb is not None and va > vb) else "B" if vb != va else "tie"
        except TypeError:
            winner = "-"
        sa = f"{va:,}" if isinstance(va, (int, float)) else str(va)
        sb = f"{vb:,}" if isinstance(vb, (int, float)) else str(vb)
        print(f"{label:<22} {sa:<22} {sb:<22} {winner:<8}")


if __name__ == "__main__":
    main()

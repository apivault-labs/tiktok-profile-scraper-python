"""
TikTok Profile Scraper — Python SDK

Official Python client for the apivault_labs/tiktok-profile-scraper Apify actor.
Extract real-time TikTok profile data: followers, likes, videos count, bio,
verification status, avatar URL and 6+ derived creator-tier signals — all
in one API call, no TikTok API key required.

Quick start:

    from tiktok_profile_scraper import TikTokProfileClient

    client = TikTokProfileClient(api_token="apify_api_xxxxxx")
    profile = client.scrape_one("khaby.lame")

    print(profile["stats"]["followers"])
    print(profile["creator_tier"])

See https://github.com/apivault-labs/tiktok-profile-scraper-python for full docs.
"""

from .client import TikTokProfileClient
from .exceptions import (
    TikTokProfileError,
    AuthenticationError,
    ActorRunError,
    ActorTimeoutError,
)

__version__ = "0.1.0"
__all__ = [
    "TikTokProfileClient",
    "TikTokProfileError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]

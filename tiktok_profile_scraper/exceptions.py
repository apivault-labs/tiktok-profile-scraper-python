"""Exception classes for the TikTok Profile Scraper SDK."""


class TikTokProfileError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(TikTokProfileError):
    """Raised when the Apify API token is missing or invalid."""


class ActorRunError(TikTokProfileError):
    """Raised when the actor run fails on Apify infrastructure."""


class ActorTimeoutError(TikTokProfileError):
    """Raised when the actor run does not finish within the allowed timeout."""

"""
TikTokProfileClient — synchronous wrapper around the Apify
``apivault_labs/tiktok-profile-scraper`` actor.

The actor handles all heavy work (HTTP, residential-proxy rotation, retries,
WAF bypass, JSON extraction from TikTok's embedded ``__UNIVERSAL_DATA_FOR_REHYDRATION__``
script) on Apify infrastructure. This client only forwards inputs, polls
until the run finishes, then downloads the dataset and decorates each record
with a few client-side derived metrics (creator tier, engagement rate).

Usage:

    from tiktok_profile_scraper import TikTokProfileClient

    client = TikTokProfileClient(api_token="apify_api_xxxxxx")
    profile = client.scrape_one("khaby.lame")
    print(profile["stats"]["followers"])
    print(profile["creator_tier"])
"""

from __future__ import annotations

import math
import os
import time
from typing import Any, Iterable

import requests

from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    TikTokProfileError,
)


ACTOR_ID = "apivault_labs~tiktok-profile-scraper"
APIFY_API_BASE = "https://api.apify.com/v2"

TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}


class TikTokProfileClient:
    """Synchronous client for the TikTok Profile Scraper Apify actor.

    Parameters
    ----------
    api_token : str, optional
        Apify Personal API token. If omitted, falls back to the
        ``APIFY_API_TOKEN`` environment variable.
    timeout : int, optional
        Maximum seconds to wait for an actor run to finish. Default 600.
    poll_interval : float, optional
        Seconds between status polls. Default 3.
    base_url : str, optional
        Override the Apify API base URL (mostly for testing).
    """

    def __init__(
        self,
        api_token: str | None = None,
        timeout: int = 600,
        poll_interval: float = 3.0,
        base_url: str = APIFY_API_BASE,
    ):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise AuthenticationError(
                "Apify API token is required. Pass api_token='apify_api_...' "
                "or set the APIFY_API_TOKEN environment variable. "
                "Get a token at https://console.apify.com/account/integrations"
            )
        self._token = token
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "tiktok-profile-scraper-python/0.1.0",
        })

    # ------------------------------------------------------------------ public

    def scrape(
        self,
        usernames: Iterable[str],
        *,
        max_retries: int = 3,
        proxy_group: str = "RESIDENTIAL",
        use_proxy: bool = True,
        actor_timeout_secs: int = 300,
        enrich: bool = True,
    ) -> list[dict[str, Any]]:
        """Run the actor synchronously and return a list of profile records.

        Parameters
        ----------
        usernames : iterable of str
            TikTok usernames to scrape (with or without leading ``@``).
        max_retries : int, optional
            Per-username retry attempts with a fresh proxy IP. Default 3.
        proxy_group : str, optional
            ``"RESIDENTIAL"`` (recommended) or ``"DATACENTER"``. Default
            ``"RESIDENTIAL"``.
        use_proxy : bool, optional
            Set to ``False`` to disable Apify proxy. Default ``True``.
        actor_timeout_secs : int, optional
            Maximum runtime hint for the actor. Default 300.
        enrich : bool, optional
            Adds client-side derived signals (``creator_tier``,
            ``engagement_rate``, ``avg_likes_per_video`` etc.) to each
            successful record. Default ``True``.

        Returns
        -------
        list[dict]
            One record per username. Failed records contain
            ``{"username": ..., "error": ...}`` instead of profile fields.

        See the README for the full output schema.
        """
        cleaned = [u.lstrip("@").strip() for u in usernames if u and u.strip()]
        if not cleaned:
            raise ValueError("usernames must contain at least one non-empty value")

        payload = {
            "usernames": cleaned,
            "maxRetries": int(max_retries),
            "proxyGroup": proxy_group,
            "useProxy": bool(use_proxy),
        }

        run_id = self._start_run(payload, actor_timeout_secs=actor_timeout_secs)
        run = self._wait_for_run(run_id)
        records = self._fetch_dataset(run["defaultDatasetId"])

        if enrich:
            records = [self._enrich(rec) for rec in records]
        return records

    def scrape_one(self, username: str, **kwargs: Any) -> dict[str, Any]:
        """Convenience wrapper for a single-profile scrape.

        Returns the first (and only) record. Raises ``ActorRunError`` if no
        record is produced (e.g. the username is invalid or TikTok blocked
        the request after all retries).
        """
        results = self.scrape([username], **kwargs)
        if not results:
            raise ActorRunError(
                f"Actor returned no records for {username!r} — "
                "the username might be invalid or TikTok blocked all retries."
            )
        rec = results[0]
        if "error" in rec and "stats" not in rec:
            raise ActorRunError(
                f"Profile @{username} failed: {rec.get('error')}"
            )
        return rec

    def estimate_cost(self, profile_count: int) -> float:
        """Return the estimated USD cost for scraping ``profile_count`` profiles.

        Pricing is $0.001 per profile (= $1 / 1000 profiles).
        """
        return round(profile_count * 0.001, 4)

    # ------------------------------------------------------------------ private

    @staticmethod
    def _enrich(rec: dict[str, Any]) -> dict[str, Any]:
        """Add a few cheap derived signals computed on the client side."""
        if not isinstance(rec, dict) or "stats" not in rec:
            return rec

        stats = rec.get("stats") or {}
        followers = int(stats.get("followers") or 0)
        likes = int(stats.get("likes") or 0)
        videos = int(stats.get("videos") or 0)

        # Creator tier — industry-standard buckets used by influencer agencies
        if followers >= 1_000_000:
            tier = "mega"
        elif followers >= 500_000:
            tier = "macro"
        elif followers >= 100_000:
            tier = "mid"
        elif followers >= 10_000:
            tier = "micro"
        elif followers >= 1_000:
            tier = "nano"
        else:
            tier = "starter"
        rec["creator_tier"] = tier

        # Average likes per video — proxy for content quality
        rec["avg_likes_per_video"] = round(likes / videos, 1) if videos else 0

        # Engagement rate — total likes / followers (rough but useful)
        rec["engagement_rate_pct"] = (
            round((likes / followers) * 100, 2) if followers else 0.0
        )

        # Likes-per-follower ratio — alt engagement signal
        rec["likes_per_follower"] = (
            round(likes / followers, 2) if followers else 0.0
        )

        # Influence score (0-100) — composite of followers + engagement
        if followers > 0:
            f_score = min(50, math.log10(max(followers, 1)) * 7.0)
            e_score = min(50, math.log10(max(likes / followers, 0.01) + 1) * 25.0)
            rec["influence_score"] = round(f_score + e_score)
        else:
            rec["influence_score"] = 0

        # Verified-creator flag for quick filtering
        rec["is_verified"] = bool(rec.get("verified", False))

        # Profile URL for downstream use
        if rec.get("username") and "profile_url" not in rec:
            rec["profile_url"] = f"https://www.tiktok.com/@{rec['username']}"

        return rec

    def _start_run(self, payload: dict[str, Any], actor_timeout_secs: int) -> str:
        url = f"{self._base_url}/acts/{ACTOR_ID}/runs"
        params = {"timeout": int(actor_timeout_secs)}
        try:
            r = self._session.post(url, params=params, json=payload, timeout=30)
        except requests.RequestException as e:
            raise TikTokProfileError(f"Failed to start actor run: {e}") from e

        if r.status_code == 401:
            raise AuthenticationError(
                "Apify rejected the API token. Generate a new one at "
                "https://console.apify.com/account/integrations"
            )
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when starting run: {r.text[:300]}"
            )

        data = r.json().get("data") or {}
        run_id = data.get("id")
        if not run_id:
            raise ActorRunError(f"Apify response missing run id: {r.text[:300]}")
        return run_id

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/actor-runs/{run_id}"
        deadline = time.time() + self._timeout
        while True:
            try:
                r = self._session.get(url, timeout=30)
            except requests.RequestException as e:
                raise TikTokProfileError(f"Failed to poll run status: {e}") from e

            if r.status_code >= 400:
                raise ActorRunError(
                    f"Apify returned HTTP {r.status_code} when polling run: {r.text[:300]}"
                )

            run = r.json().get("data") or {}
            status = run.get("status")
            if status in TERMINAL_OK:
                return run
            if status in TERMINAL_FAIL:
                raise ActorRunError(
                    f"Actor run {run_id} ended with status={status}: "
                    f"{run.get('statusMessage') or '(no message)'}"
                )

            if time.time() > deadline:
                raise ActorTimeoutError(
                    f"Actor run {run_id} did not finish within {self._timeout}s "
                    f"(last status={status}). The run may still be running on Apify; "
                    "increase `timeout=` or fetch the dataset manually."
                )

            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset_id}/items"
        params = {"clean": "true", "format": "json"}
        try:
            r = self._session.get(url, params=params, timeout=120)
        except requests.RequestException as e:
            raise TikTokProfileError(f"Failed to download dataset: {e}") from e

        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when fetching dataset: "
                f"{r.text[:300]}"
            )

        try:
            data = r.json()
        except ValueError as e:
            raise ActorRunError(f"Apify dataset is not valid JSON: {e}") from e

        if not isinstance(data, list):
            raise ActorRunError(
                f"Unexpected dataset payload (not a list): {type(data).__name__}"
            )
        return data

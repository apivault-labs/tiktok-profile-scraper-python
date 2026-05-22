# TikTok Profile Scraper — Python SDK

> **Real-time TikTok profile data without an API key: followers, likes, videos count, bio, verification status, avatar URL, plus 6 derived creator-tier signals — all in one call.**

Python client for the [TikTok Profile Scraper Apify Actor](https://apify.com/apivault_labs/tiktok-profile-scraper) — extract structured profile data from any public TikTok account at **$0.001 per profile**, with built-in residential-proxy rotation and retries.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue?logo=apify)](https://apify.com/apivault_labs/tiktok-profile-scraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![PyPI-friendly](https://img.shields.io/badge/install-pip-success)](#installation)

---

## What it does

For any public TikTok username, this actor fetches the profile page, extracts the embedded JSON state and returns a single rich record combining **all profile metadata** + **6 derived creator-tier signals** computed by the SDK.

A direct, pay-per-use alternative to:
- TikTok Business / Research API (rate-limited, app review required, US-only research access)
- Manual TikTok scraping (heavy WAF, breaks weekly)
- Generic influencer-discovery platforms ($99-$499/mo)

**Pricing:** $0.001 per profile. No subscriptions, no expiring credits, no rate limits.

---

## Quick start

```python
from tiktok_profile_scraper import TikTokProfileClient

client = TikTokProfileClient(api_token="apify_api_xxxxxx")

profile = client.scrape_one("khaby.lame")

print(f"Name:        {profile['nickname']}")
print(f"Verified:    {profile['verified']}")
print(f"Followers:   {profile['stats']['followers']:,}")
print(f"Likes:       {profile['stats']['likes']:,}")
print(f"Videos:      {profile['stats']['videos']:,}")
print(f"Tier:        {profile['creator_tier']}")
print(f"Engagement:  {profile['engagement_rate_pct']}%")
print(f"Influence:   {profile['influence_score']}/100")
```

Output:
```
Name:        Khabane lame
Verified:    True
Followers:   160,327,702
Likes:       2,567,849,339
Videos:      1,311
Tier:        mega
Engagement:  1601.63%
Influence:   81/100
```

---

## Installation

```bash
pip install git+https://github.com/apivault-labs/tiktok-profile-scraper-python.git
```

Or clone and use directly:

```bash
git clone https://github.com/apivault-labs/tiktok-profile-scraper-python.git
cd tiktok-profile-scraper-python
pip install -r requirements.txt
```

Requires Python 3.9+ and the [`requests`](https://pypi.org/project/requests/) library.

---

## Get your API token (free)

1. Sign up at [apify.com](https://apify.com) — free tier includes $5 monthly credits, no card required
2. Go to [Account → Integrations](https://console.apify.com/account/integrations)
3. Copy your Personal API token

```bash
export APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx
```

Or pass it explicitly:

```python
client = TikTokProfileClient(api_token="apify_api_xxxxxx")
```

---

## What you get for $0.001 per profile

### 👤 Core profile fields (real-time, no cache)
- `username`, `uniqueId`, `nickname`, `id`, `secUid`
- `verified` — blue checkmark status
- `privateAccount` — private profile flag
- `signature` — full bio text
- `avatar` — full-resolution profile picture URL

### 📊 Statistics block
- `stats.followers` — follower count
- `stats.following` — following count
- `stats.likes` — total likes (heart count) across all videos
- `stats.videos` — total videos posted
- `stats.friends` — mutual-follow count

### 🧠 Derived creator-tier signals (added by the SDK)
- **`creator_tier`** — `mega` / `macro` / `mid` / `micro` / `nano` / `starter` (industry-standard buckets)
- **`influence_score`** (0-100) — composite of followers × engagement, log-scaled
- **`engagement_rate_pct`** — total likes ÷ followers × 100
- **`avg_likes_per_video`** — total likes ÷ videos count
- **`likes_per_follower`** — alt engagement metric
- **`is_verified`** — typed boolean
- **`profile_url`** — canonical TikTok URL

---

## Examples

See the [`examples/`](examples) folder for full code:

| File | What it does |
|---|---|
| [`quickstart.py`](examples/quickstart.py) | Scrape one profile, print key metrics |
| [`bulk_scrape.py`](examples/bulk_scrape.py) | Scrape 100+ profiles in one batch |
| [`find_micro_influencers.py`](examples/find_micro_influencers.py) | Filter creators by tier and engagement |
| [`verified_only.py`](examples/verified_only.py) | Keep only verified accounts |
| [`export_to_csv.py`](examples/export_to_csv.py) | Save flat profiles to CSV / Excel |
| [`competitor_overlap.py`](examples/competitor_overlap.py) | Compare two creators side-by-side |
| [`influencer_outreach_list.py`](examples/influencer_outreach_list.py) | Build a ranked outreach shortlist |

---

## API reference

### `TikTokProfileClient(api_token=None, timeout=600)`

| Param | Type | Description |
|---|---|---|
| `api_token` | `str` | Apify API token. Falls back to `APIFY_API_TOKEN` env var. |
| `timeout` | `int` | Max seconds to wait for the actor run. Default 600 (10 min). |
| `poll_interval` | `float` | Seconds between status polls. Default 3. |

### `client.scrape(usernames, **kwargs)`

Scrape multiple profiles synchronously.

| Param | Type | Default | Description |
|---|---|---|---|
| `usernames` | `list[str]` | required | TikTok usernames (with or without `@`) |
| `max_retries` | `int` | 3 | Retry attempts per profile with new proxy IP |
| `proxy_group` | `str` | `"RESIDENTIAL"` | `"RESIDENTIAL"` or `"DATACENTER"` |
| `use_proxy` | `bool` | `True` | Disable proxy entirely if `False` |
| `actor_timeout_secs` | `int` | 300 | Actor runtime hint passed to Apify |
| `enrich` | `bool` | `True` | Add client-side `creator_tier`, `engagement_rate_pct`, etc. |

Returns: `list[dict]` — one record per username. Failed records contain `{"username": ..., "error": ...}` instead of profile fields.

### `client.scrape_one(username, **kwargs)`

Convenience wrapper for a single profile. Returns one `dict` or raises `ActorRunError`.

### `client.estimate_cost(profile_count)`

Returns the estimated USD cost (`profile_count × 0.001`).

---

## Sample output

```json
{
  "username": "khaby.lame",
  "id": "6974449150902150149",
  "nickname": "Khabane lame",
  "uniqueId": "khaby.lame",
  "verified": true,
  "privateAccount": false,
  "signature": "Se vuoi ridere sei nel posto giusto\ud83d\ude0e",
  "secUid": "MS4wLjABAAAAwAg0rSzO65WQfz4RzQ...",
  "avatar": "https://p16-sign-va.tiktokcdn.com/...",
  "stats": {
    "followers": 160327702,
    "following": 85,
    "likes": 2567849339,
    "videos": 1311,
    "friends": 0
  },
  "creator_tier": "mega",
  "influence_score": 81,
  "engagement_rate_pct": 1601.63,
  "avg_likes_per_video": 1958695.1,
  "likes_per_follower": 16.02,
  "is_verified": true,
  "profile_url": "https://www.tiktok.com/@khaby.lame"
}
```

---

## Use cases

### 🎯 Influencer Marketing
Build creator shortlists by exact criteria:
- `creator_tier == "micro"` — proven engagement at affordable rates
- `engagement_rate_pct > 5` — filter out follower-bot accounts
- `verified == True` — brand-safe partners only
- `stats.videos > 50` — active creators with content history

### 🏷️ Brand Safety & Vetting
Pre-screen UGC partners before signing contracts:
- Verify follower counts (no buy-followers fraud)
- Check `privateAccount` status
- Inspect `signature` for blacklisted brands or redirects
- Validate `verified` badge

### 📊 Competitive Intelligence
Track competitor profiles over time:
- Daily snapshots of follower / likes / videos
- Detect viral spikes via stat deltas
- Benchmark `engagement_rate_pct` across category leaders
- Map verified-vs-unverified positioning

### 🔍 Talent Discovery
Find rising creators in specific niches:
- Filter `nano` and `micro` tiers by engagement rate
- Look for `verified` accounts with low follower count (early breakouts)
- Cross-reference avatar / bio text for niche keywords

### 📈 Analytics Dashboards
Pipe profile snapshots into:
- Power BI / Tableau / Looker
- Internal CRMs and ATS systems
- Custom influencer-relationship management tools

### 🤖 AI / LLM Training Data
Populate datasets for:
- Influencer category classification
- Bio-text NLP / topic modeling
- Profile-quality scoring models

---

## Pricing

Pay only for what you scrape:

| Volume | Cost |
|---|---|
| 1 profile | $0.001 |
| 1,000 profiles | $1.00 |
| 10,000 profiles | $10.00 |
| 100,000 profiles | $100.00 |

Free Apify tier includes ~$5 monthly credit — scrape up to **5,000 TikTok profiles per month for free**.

---

## How it works

All data comes from **public TikTok pages** — no logins, no session cookies, no TikTok API key:

1. **HTTP fetch** of `https://www.tiktok.com/@{username}` via Apify residential proxy
2. **JSON extraction** from the embedded `<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">` block
3. **Fallback** to legacy `<script id="SIGI_STATE">` for older pages
4. **Retry rotation** — up to 3 retries with a fresh proxy IP on each WAF block
5. **Client-side enrichment** — SDK adds creator-tier and engagement signals from the raw stats

Influence-score formula:
```
followers_score = min(50, log10(followers) × 7)
engagement_score = min(50, log10(likes/followers + 1) × 25)
influence_score = followers_score + engagement_score    # 0-100
```
A 1M-follower creator with healthy engagement scores ~75; bot accounts with empty content score under 25.

---

## Speed & reliability

- **5–15 seconds per profile** (HTTP only, no rendering)
- **Residential proxy by default** — survives TikTok's WAF reliably
- **3 retries per username** with fresh IP rotation
- **Graceful failure** — if all retries exhaust, the record contains `{"username": ..., "error": ...}` instead of crashing the whole run

---

## FAQ

**Q: Do I need a TikTok API key?**
A: No. This actor uses public TikTok profile pages, not the official API. No app review, no rate quota, no US-only access restrictions.

**Q: How fresh is the data?**
A: 100% real-time. No caching layer. Each call hits TikTok's live profile page.

**Q: Can it scrape video lists?**
A: Not in this actor — it returns profile metadata only (faster + cheaper). For video-level data, see the companion [TikTok Shop Scraper](https://apify.com/apivault_labs/tiktok-shop-scraper) or watch this repo for a future `tiktok-videos-scraper`.

**Q: What about private accounts?**
A: Private profiles return limited data (no stats, no signature) but the call still succeeds with whatever public fields are available.

**Q: Will it work on every username?**
A: Any public TikTok account. Banned / deleted accounts return an `error` field. Username typos return `error="No user info found"`.

**Q: Is the `engagement_rate_pct` reliable?**
A: It's the lifetime ratio of total likes to current followers. For a more granular per-post engagement rate, you'd need a video-level scrape — but this lifetime ratio is the standard quick-screen metric used by influencer agencies.

**Q: Can I run this without Apify?**
A: This package is a thin wrapper around the hosted actor. The actor handles the residential proxy, retries and TikTok WAF mitigation. Self-hosted TikTok scraping at scale requires premium proxies + JS rendering — usually not worth building yourself.

**Q: Is this allowed by TikTok's ToS?**
A: This actor only reads publicly accessible profile pages, the same data any browser sees. As with any scraping, use responsibly and respect TikTok's Terms of Service for your jurisdiction.

---

## Related Apify actors

- [TikTok Shadow Ban Checker](https://apify.com/apivault_labs/tiktok-shadow-ban-checker) — instant `indexEnabled` check for any video
- [TikTok Shop Scraper](https://apify.com/apivault_labs/tiktok-shop-scraper) — product listings from TikTok Shop
- [Instagram Profile Scraper](https://apify.com/apivault_labs/instagram-profile-scraper) — same pattern for Instagram
- [Reddit Profile Scraper](https://apify.com/apivault_labs/reddit-scraper) — Reddit user metadata

See [all actors by apivault_labs](https://apify.com/apivault_labs).

---

## License

MIT — see [LICENSE](LICENSE).

This client is open source. The underlying Apify actor is a paid service ($0.001/profile).

---

## Keywords

`tiktok-scraper` `tiktok-api` `tiktok-profile-scraper` `tiktok-followers-api` `tiktok-without-api-key` `tiktok-no-key` `tiktok-research-api-alternative` `influencer-marketing` `influencer-discovery` `creator-tier` `engagement-rate-api` `social-media-scraper` `social-media-analytics` `creator-economy` `ugc-vetting` `brand-safety` `tiktok-bio-scraper` `tiktok-stats-api` `web-scraping` `apify` `apify-actor` `python-sdk`

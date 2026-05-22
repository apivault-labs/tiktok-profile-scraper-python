# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] — 2026-05-22

### Added
- Initial release of the Python SDK
- `TikTokProfileClient` with synchronous `scrape()` and `scrape_one()` methods
- Forwarding of all four actor inputs:
  `usernames`, `maxRetries`, `proxyGroup`, `useProxy`
- Client-side enrichment (`enrich=True` by default):
  `creator_tier`, `influence_score`, `engagement_rate_pct`,
  `avg_likes_per_video`, `likes_per_follower`, `is_verified`, `profile_url`
- 7 example scripts: quickstart, bulk scrape, micro-influencer filter,
  verified-only filter, CSV export, competitor overlap, outreach list
- MIT license

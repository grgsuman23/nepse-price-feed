# NEPSE price feed

A GitHub Action fetches today's prices and the company/sector list from **nepalstock.com** every 15 minutes during market hours (Sun–Thu, 10:45–15:30 Nepal time) and publishes them as `prices.json`.
Scrips that didn't trade today keep their last known price.

**Feed URL:** https://raw.githubusercontent.com/grgsuman23/nepse-price-feed/main/prices.json

Used by the Promoter Share Portfolio app (**Prices & Settings → GitHub price feed**) and available to other tools such as Nepse-Screener.

## Format
```json
{
  "src": "nepalstock.com",
  "at": "2026-11-23T09:15:00+00:00",
  "p": [["SYMBOL", ltp, previousClose, percentChange, businessDate], ...],
  "c": [["SYMBOL", "Company name", "Sector"], ...]
}
```

- Public market data only. Never commit holdings or personal data here.
- Manual refresh: **Actions → NEPSE price feed → Run workflow**.
- Uses the open-source [NepseUnofficialApi](https://github.com/basic-bgnr/NepseUnofficialApi) client for nepalstock.com's token handshake.

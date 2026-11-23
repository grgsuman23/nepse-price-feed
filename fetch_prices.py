"""
Fetch today's NEPSE prices (and the company/sector list) from nepalstock.com
and write prices.json for the Promoter Share Portfolio app.

Runs in GitHub Actions (see .github/workflows/nepse-prices.yml).
Uses the open-source NepseUnofficialApi client for nepalstock.com's token handshake.
Only public market data is written. Never put your holdings in this repo.
"""
import datetime
import json
import pathlib
import sys

from nepse import Nepse

OUT = pathlib.Path("prices.json")


def client():
    n = Nepse()
    try:
        n.getMarketStatus()
    except Exception:
        # nepalstock.com has at times served an incomplete TLS chain; public data only.
        n.setTLSVerification(False)
    return n


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    n = client()
    data = n.getPriceVolume()
    if isinstance(data, dict):
        data = data.get("content") or data.get("data") or []
    rows = []
    for r in data:
        sym = (r.get("symbol") or "").strip().upper()
        ltp = num(r.get("lastTradedPrice")) or num(r.get("closePrice")) or num(r.get("previousClose"))
        if not sym or not ltp:
            continue
        prev = num(r.get("previousClose"))
        pct = num(r.get("percentageChange"))
        if pct is None and prev:
            pct = round((ltp - prev) / prev * 100, 2)
        rows.append([sym, ltp, prev or "", "" if pct is None else pct, r.get("businessDate") or ""])
    if not rows:
        sys.exit("No price rows returned; keeping the previous prices.json")

    companies = []
    try:
        for c in n.getCompanyList():
            if c.get("symbol"):
                companies.append([c["symbol"].upper(), c.get("companyName", ""), c.get("sectorName", "")])
    except Exception as e:  # company list is optional
        print("company list failed:", e)

    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    # nepalstock.com lists only scrips traded today: keep the last known price for the rest
    today = {r[0] for r in rows}
    rows += [r for r in old.get("p", []) if r and r[0] not in today]
    rows.sort(key=lambda r: r[0])
    if old.get("p") == rows and (not companies or old.get("c") == companies):
        print(f"No change in {len(rows)} prices; not rewriting")
        return
    out = {
        "src": "nepalstock.com",
        "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "p": rows,
        "c": companies or old.get("c", []),
    }
    OUT.write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False))
    print(f"Wrote {len(rows)} prices, {len(out['c'])} companies")


if __name__ == "__main__":
    main()

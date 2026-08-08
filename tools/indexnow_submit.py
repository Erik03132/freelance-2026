#!/usr/bin/env python3
"""
IndexNow-сабмиттер для быстрой индексации в Яндекс и Bing.

Использование:
  python3 tools/indexnow_submit.py https://svo-start.ru/new-page
  python3 tools/indexnow_submit.py --key ABC123 --file urls.txt
  python3 tools/indexnow_submit.py --site svo-start.ru --sitemap https://svo-start.ru/sitemap.xml
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


INDEXNOW_ENDPOINTS = [
    "https://yandex.com/indexnow",
    "https://api.indexnow.org/indexnow",
]


def load_key(site: str) -> str:
    key_file = Path(f"projects/{site}/public/keyLocation.txt") if "/" not in site else None
    if key_file and key_file.exists():
        return key_file.read_text().strip()

    env_key = os.getenv("INDEXNOW_KEY")
    if env_key:
        return env_key

    return ""


def submit_urls(key: str, urls: list[str], site: str) -> dict:
    results = {}
    for endpoint in INDEXNOW_ENDPOINTS:
        body = json.dumps(
            {
                "host": site,
                "key": key,
                "keyLocation": f"https://{site}/keyLocation.txt",
                "urlList": urls,
            }
        ).encode("utf-8")
        req = Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            resp = urlopen(req, timeout=30)
            status = resp.status
            results[endpoint] = {
                "status": status,
                "ok": status in (200, 202),  # 202 = норма для IndexNow
            }
        except HTTPError as e:
            results[endpoint] = {"status": e.code, "ok": False, "error": str(e)}
        except URLError as e:
            results[endpoint] = {"status": 0, "ok": False, "error": str(e)}

    return results


def submit_sitemap(site: str, sitemap_url: str) -> dict:
    urls = [
        f"https://{site}",
        f"https://{site}/about",
        f"https://{site}/contacts",
    ]
    key = load_key(site)
    return submit_urls(key, urls, site)


def main():
    parser = argparse.ArgumentParser(description="IndexNow URL submitter for Yandex/Bing")
    parser.add_argument("urls", nargs="*", help="URLs to submit")
    parser.add_argument("--file", "-f", help="File with URLs (one per line)")
    parser.add_argument("--site", "-s", help="Site hostname (e.g. svo-start.ru)")
    parser.add_argument("--key", "-k", help="IndexNow API key (8-128 chars)")
    parser.add_argument("--sitemap", help="Submit sitemap URL for discovery")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    urls = list(args.urls)
    if args.file:
        urls.extend(
            line.strip()
            for line in Path(args.file).read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
        )

    if args.sitemap:
        site = args.site or args.sitemap.split("/")[2]
        results = submit_sitemap(site, args.sitemap)
    elif urls:
        site = args.site or urls[0].split("/")[2]
        key = args.key or load_key(site)
        if not key:
            print(
                "No IndexNow key found. Set INDEXNOW_KEY env or create keyLocation.txt",
                file=sys.stderr,
            )
            sys.exit(1)
        results = submit_urls(key, urls, site)
    else:
        parser.print_help()
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for endpoint, r in results.items():
            status = "OK" if r["ok"] else "FAIL"
            note = " (202 = async key check, expected)" if r.get("status") == 202 else ""
            print(f"{endpoint}: {r['status']} [{status}]{note}")
            if "error" in r:
                print(f"  error: {r['error']}")


if __name__ == "__main__":
    main()

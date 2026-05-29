"""
discover_companies.py

Goal:
- take a list of company names
- try to discover their careers/job-board URLs
- classify the job board type
- save results into companies.json

This script uses:
- Google Search API HTML search
- simple pattern matching

No API keys required.

Install:
    pip install requests beautifulsoup4

Run:
    python discover_companies.py

Output:
    companies.json
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict
from typing import List, Optional
import os

import requests
from bs4 import BeautifulSoup


# -----------------------------------
# CONFIG
# -----------------------------------


# list of company names to discover
COMPANY_NAMES = [
    "Stripe",
    "Figma",
    "Google",
    "Amazon",
    "Meta",
    "Netflix",
    "Datadog",
    "Databricks",
    "CapitalOne",
    "Notion"
]


# read output into this file
OUTPUT_FILE = "companies.json"

# delay to avoid hitting rate limits
SEARCH_DELAY_SECONDS = 2


# -----------------------------------
# MODELS
# -----------------------------------


## structure to hold the retrieved company info
@dataclass
class CompanyRecord:
    company: str
    url: str
    source_type: str


# -----------------------------------
# HELPERS
# -----------------------------------

# source type detection based on patterns found in URL
def detect_source_type(url: str) -> str:

    url = url.lower()

    if "greenhouse.io" in url:
        return "greenhouse"

    if "lever.co" in url:
        return "lever"

    if "ashbyhq.com" in url:
        return "ashby"

    if "workday" in url:
        return "workday"

    return "generic"


# remove any unnecessary query parameters or fragments from the URL
def clean_url(url: str) -> str:
    url = url.strip()

    # remove tracking fragments
    url = url.split("?")[0]
    url = url.split("#")[0]

    return url


SERP_API_KEY = os.getenv("SERP_API_KEY")


def google_search(query: str):
    url = "https://serpapi.com/search"

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    results = data.get("organic_results", [])

    for result in results:
        print(result)
        link = result.get("link")

        if not link:
            continue

        link_lower = link.lower()
        clean_url(link_lower)

        if any(
            pattern in link_lower
            for pattern in [
                "search"
                "job-search",
                "jobs/search",
                "all-jobs",
                "open-positions",
                "careers",
                "careers/search",
                "openings",
            ]
        ):
            return link

    return None

# -----------------------------------
# MAIN DISCOVERY LOGIC
# -----------------------------------

def discover_company(company_name: str) -> Optional[CompanyRecord]:
    print(f"[searching] {company_name}")


    ## Google's HTML search is more likely to find the careers page than DuckDuckGo's API
    queries = [
        f"{company_name} see open job listings",
    ]

    for query in queries:
        try:
            url = google_search(query)

            if not url:
                continue

            source_type = detect_source_type(url)

            print(f"  found: {url}")

            return CompanyRecord(
                company=company_name,
                url=url,
                source_type=source_type,
            )

        except Exception as e:
            print(f"  error: {e}")

    print("  no result found")
    return None


def main() -> None:
    records: List[CompanyRecord] = []

    for company in COMPANY_NAMES:
        record = discover_company(company)

        if record:
            records.append(record)

        time.sleep(SEARCH_DELAY_SECONDS)

    output = [asdict(r) for r in records]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved {len(records)} companies to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

"""
discover_companies.py

Goal:
- take a list of company names
- try to discover their careers/job-board URLs
- classify the job board type
- save results into companies.json

This script uses:
- DuckDuckGo HTML search
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

import requests
from bs4 import BeautifulSoup


# -----------------------------------
# CONFIG
# -----------------------------------

COMPANY_NAMES = [
    "Stripe",
    "Figma",
    "Notion",
    "OpenAI",
    "Datadog",
]

OUTPUT_FILE = "companies.json"

SEARCH_DELAY_SECONDS = 2


# -----------------------------------
# MODELS
# -----------------------------------

@dataclass
class CompanyRecord:
    company: str
    url: str
    source_type: str


# -----------------------------------
# HELPERS
# -----------------------------------

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


def clean_url(url: str) -> str:
    url = url.strip()

    # remove tracking fragments
    url = url.split("?")[0]
    url = url.split("#")[0]

    return url


def duckduckgo_search(query: str) -> Optional[str]:
    """
    Uses DuckDuckGo HTML search.
    """
    search_url = "https://html.duckduckgo.com/html/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; CareerAgent/1.0)"
        )
    }

    response = requests.post(
        search_url,
        data={"q": query},
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    results = soup.select(".result__a")

    for result in results:
        href = result.get("href")

        if not href:
            continue

        href = clean_url(href)

        # prioritize common careers platforms
        if any(
            keyword in href.lower()
            for keyword in [
                "greenhouse",
                "lever",
                "ashby",
                "careers",
                "jobs",
            ]
        ):
            return href

    return None


# -----------------------------------
# MAIN DISCOVERY LOGIC
# -----------------------------------

def discover_company(company_name: str) -> Optional[CompanyRecord]:
    print(f"[searching] {company_name}")

    queries = [
        f"{company_name} careers",
        f"{company_name} jobs",
        f"{company_name} greenhouse",
        f"{company_name} lever",
    ]

    for query in queries:
        try:
            url = duckduckgo_search(query)

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

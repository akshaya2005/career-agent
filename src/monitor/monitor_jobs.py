from fetcher import fetch_html
from extractor import extract_jobs
from storage import load_seen_jobs, save_seen_jobs

import json

def load_companies():
    with open("../companies/companies.json") as f:
        return json.load(f)


def monitor():
    companies = load_companies()

    seen = load_seen_jobs()

    new_jobs = []
    
    for company in companies:
        html = fetch_html(company["url"])
        jobs = extract_jobs(company, html)
        
        for job in jobs:
            job_id = job["url"]
            if job_id in seen:
                continue

            seen.add(job_id)
            new_jobs.append(job)

    
    save_seen_jobs(seen)
    return new_jobs


if __name__ == "__main__":
    load_companies()
    new_jobs = monitor()


from bs4 import BeautifulSoup
from urllib.parse import urljoin


JOB_KEYWORDS = ["engineer", "developer", "scientist", "analyst", "manager", "designer", "intern", "software"]

def looks_like_job_title(text):
    text = text.lower()

    return any (
        keyword in text
        for keyword in JOB_KEYWORDS
    )

def extract_jobs(company, html):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for link in soup.find_all("a", href=True):
        title = link.get_text(" ", strip=True)
        if not title:
            continue
        if not looks_like_job_title(title):
            continue
        jobs.append({
            "company": company["company"],
            "title": title,
            "url": urljoin(
                company["url"],
                link["href"]
            )
        })
    
    return jobs
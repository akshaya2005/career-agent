import requests 

def fetch_html(url):
    response = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": "career-agent"
        }
    )

    response.raise_for_status()
    return response.text
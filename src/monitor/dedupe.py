import json

def load_seen_jobs():
    with open(
        "seen_jobs.json"
    ) as f:
        data = json.load(f)
    
    return set(data["seen_jobs"])


def save_seen_jobs(seen):
    with open(
        "seen_jobs.json", "w"
    ) as f:
        json.dump({
            "seen_jobs":list(seen)
            },
            f,
            indent=2
        )
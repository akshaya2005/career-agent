import json
import os

def load_seen_jobs():
    # File doesn't exist
    if not os.path.exists("seen_jobs.json"):
        return set()

    try:
        with open("seen_jobs.json", "r") as f:
            content = f.read().strip()

            # Empty file
            if not content:
                return set()

            data = json.loads(content)

            # Missing key
            if "seen_jobs" not in data:
                return set()

            return set(data["seen_jobs"])

    except (json.JSONDecodeError, IOError):
        # Malformed JSON or read error
        return set()


def save_seen_jobs(seen):
    with open("seen_jobs.json", "w") as f:
        json.dump(
            {
                "seen_jobs": list(seen)
            },
                f,
                indent=2
        )
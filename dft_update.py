import requests
import datetime
import base64
import os

# -----------------------------
# CONFIG
# -----------------------------
API_URL = "https://cdn-nfs.faireconomy.media/ff_calendar_thisweek.json"

GITHUB_REPO = "trade4beri2/beri-news"
GITHUB_FILE_PATH = "news.csv"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

DAYS_AHEAD = 14

# -----------------------------
# Fetch DFT/FF events
# -----------------------------
def fetch_dft_events():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    return response.json()

# -----------------------------
# Convert event to CSV row
# -----------------------------
def convert_event_to_csv_row(event):
    ts = int(event["timestamp"])
    dt = datetime.datetime.utcfromtimestamp(ts)
    dt_str = dt.strftime("%Y.%m.%d %H:%M")

    currency = event.get("country", "UNK")
    impact = event.get("impact", "DFT")
    title = event.get("title", "EVENT")

    return f"{dt_str};{currency};{impact};{title}"

# -----------------------------
# Update GitHub file
# -----------------------------
def update_github_file(csv_content):
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

    # Get current file SHA
    get_resp = requests.get(api_url, headers={
        "Authorization": f"token {GITHUB_TOKEN}"
    })
    get_resp.raise_for_status()
    sha = get_resp.json()["sha"]

    # Base64 encode content
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")

    # Upload new version
    put_resp = requests.put(api_url, json={
        "message": "Auto-update news.csv (DFT 14 days)",
        "content": encoded_content,
        "sha": sha
    }, headers={
        "Authorization": f"token {GITHUB_TOKEN}"
    })

    put_resp.raise_for_status()

# -----------------------------
# Main logic
# -----------------------------
def main():
    events = fetch_dft_events()

    now = datetime.datetime.utcnow()
    end_date = now + datetime.timedelta(days=DAYS_AHEAD)

    rows = []

    for event in events:
        ts = int(event["timestamp"])
        dt = datetime.datetime.utcfromtimestamp(ts)

        if now <= dt <= end_date:
            rows.append(convert_event_to_csv_row(event))

    csv_output = "\n".join(rows)

    update_github_file(csv_output)

    print("news.csv successfully updated.")

if __name__ == "__main__":
    main()

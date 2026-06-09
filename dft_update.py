import requests
import datetime
import base64
import json
import os

# -----------------------------
# CONFIG
# -----------------------------
# ForexFactory / DailyFX API (DFT is ezt használja)
API_URL = "https://cdn-nfs.faireconomy.media/ff_calendar_thisweek.json"

# GitHub repo info
GITHUB_REPO = "trade4beri2/beri-news"
GITHUB_FILE_PATH = "news.csv"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # GitHub Actions automatikusan betölti

# Hány napot kérünk a mai naptól
DAYS_AHEAD = 14

# -----------------------------
# DFT adat lekérése
# -----------------------------
def fetch_dft_events():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    return response.json()

# -----------------------------
# DFT → CSV sor konverzió
# -----------------------------
def convert_event_to_csv_row(event):
    # DFT timestamp → datetime
    ts = int(event["timestamp"])
    dt = datetime.datetime.utcfromtimestamp(ts)

    # CSV formátum: YYYY.MM.DD HH:MM
    dt_str = dt.strftime("%Y.%m.%d %H:%M")

    # Deviza (pl. USD, EUR)
    currency = event.get("country", "UNK")

    # Impact (DFT szabályzat szerint nem csak piros!)
    impact = event.get("impact", "DFT")

    # Esemény neve
    title = event.get("title", "EVENT")

    return f"{dt_str};{currency};{impact};{title}"

# -----------------------------
# GitHub fájl frissítése
# -----------------------------
def update_github_file(csv_content):
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

    # Először le kell kérni a fájl SHA-ját
    get_resp = requests.get(api_url, headers={
        "Authorization": f"token {GITHUB_TOKEN}"
    })
    get_resp.raise_for_status()
    sha = get_resp.json()["sha"]

    # Base64 kódolás (GitHub API így várja)
    encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")

    # Feltöltés (felülírás)
    put_resp = requests.put(api_url, json={
        "message": "Auto-update news.csv (DFT 14 days)",
        "content": encoded_content,
        "sha": sha
    }, headers={
        "Authorization": f"token {GITHUB_TOKEN}"
    })

    put_resp.raise

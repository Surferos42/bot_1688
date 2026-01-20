from playwright.sync_api import sync_playwright
from datetime import datetime
import requests
import os
import time

WEBHOOK = os.getenv("DISCORD_WEBHOOK")
URL = "https://www.1688.com/"

def send_to_discord(message):
    requests.post(WEBHOOK, json={"content": message})

def run():
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="zh-CN")

        page.goto(URL, timeout=60000)
        time.sleep(5)

        for _ in range(6):
            page.mouse.wheel(0, 3000)
            time.sleep(2)

        for a in page.query_selector_all("a"):
            try:
                text = a.inner_text().replace("\n", " ")
                if "销量" in text:
                    products.append(text)
            except:
                pass

        browser.close()

    top50 = products[:50]
    date = datetime.now().strftime("%Y-%m-%d")

    message = f"🔥 **1688 TOP 50 — {date}** 🔥\n\n"
    for i, p in enumerate(top50, 1):
        message += f"**{i}.** {p}\n"

        if len(message) > 1800:
            send_to_discord(message)
            message = ""

    if message:
        send_to_discord(message)

if __name__ == "__main__":
    run()

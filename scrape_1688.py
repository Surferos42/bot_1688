from playwright.sync_api import sync_playwright
from datetime import datetime
import requests
import os
import time

# Pobieramy webhook z sekretów GitHub
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# URL do hot-selling produktów 1688
URL = "https://s.1688.com/selloffer/offer_search.htm?keywords=%E7%83%AD%E9%94%80&sortType=saleDesc"

def send_to_discord(message):
    """Wyślij wiadomość do Discorda, jeśli webhook istnieje"""
    if not WEBHOOK:
        print("❌ BRAK DISCORD_WEBHOOK")
        return
    requests.post(WEBHOOK, json={"content": message})

def run():
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="zh-CN")
        page.goto(URL, timeout=60000)

        # Scrollujemy, żeby załadować produkty
        for _ in range(6):
            page.mouse.wheel(0, 3000)
            time.sleep(2)

        # Pobieramy wszystkie linki
        for a in page.query_selector_all("a"):
            try:
                text = a.inner_text().replace("\n", " ")
                href = a.get_attribute("href")
                if not href:
                    continue

                # sprawdzamy, czy to produkt z info o sprzedaży
                if "已售" in text or "成交" in text:
                    # poprawiamy linki względne
                    if href.startswith("//"):
                        href = "https:" + href
                    elif href.startswith("/"):
                        href = "https://www.1688.com" + href

                    products.append({
                        "text": text,
                        "link": href
                    })
            except:
                continue

        browser.close()

    # Bierzemy TOP 50
    top50 = products[:50]

    print(f"Znaleziono produktów: {len(top50)}")

    # Budujemy wiadomość Discord
    date = datetime.now().strftime("%Y-%m-%d")
    message = f"🔥 **1688 TOP 50 — {date}** 🔥\n\n"

    for i, p in enumerate(top50, 1):
        message += f"**{i}.** {p['text']}\n🔗 {p['link']}\n\n"

        # Limit długości wiadomości Discord ~2000 znaków
        if len(message) > 1800:
            send_to_discord(message)
            message = ""

    # Wyślij ostatnią wiadomość
    if message:
        send_to_discord(message)

if __name__ == "__main__":
    run()

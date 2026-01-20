from playwright.sync_api import sync_playwright
from datetime import datetime
import requests
import os
import time

# Pobieramy webhook z sekretów GitHub
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# URL hot-selling produktów (sortowanie po sprzedaży)
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

        # Scrollowanie strony, żeby załadować produkty (lazy loading)
        for _ in range(6):
            page.mouse.wheel(0, 3000)
            time.sleep(2)

        # Szukamy produktów w odpowiednich divach
        for item in page.query_selector_all("div.offer-title"):
            try:
                title_el = item.query_selector("a")
                sale_el = item.query_selector("span.sale-num")

                if not title_el or not sale_el:
                    continue

                title_text = title_el.inner_text().strip()
                sale_text = sale_el.inner_text().strip()
                href = title_el.get_attribute("href")

                # popraw linki względne
                if href.startswith("//"):
                    href = "https:" + href
                elif href.startswith("/"):
                    href = "https://www.1688.com" + href

                products.append({
                    "text": f"{title_text} {sale_text}",
                    "link": href
                })

            except Exception as e:
                continue

        browser.close()

    # Bierzemy TOP 50
    top50 = products[:50]

    print(f"Znaleziono produktów: {len(top50)}")

    # Budujemy wiadomość do Discorda
    date = datetime.now().strftime("%Y-%m-%d")
    message = f"🔥 **1688 TOP 50 — {date}** 🔥\n\n"

    for i, p in enumerate(top50, 1):
        message += f"**{i}.** {p['text']}\n🔗 {p['link']}\n\n"

        # Limit długości wiadomości Discord ~2000 znaków
        if len(message) > 1800:
            send_to_discord(message)
            message = ""

    # Wyślij ostatnią część
    if message:
        send_to_discord(message)

if __name__ == "__main__":
    run()

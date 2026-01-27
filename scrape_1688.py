# scraper.py
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time
import random

URL = "https://s.1688.com/selloffer/offer_search.htm?keywords=usb%20cable"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/119.0.0.0 Safari/537.36",
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            viewport={"width": 1366, "height": 768}
        )

        page = context.new_page()
        stealth_sync(page)

        page.goto(URL, timeout=60000, wait_until="domcontentloaded")
        time.sleep(random.uniform(3, 6))

        if "login.1688.com" in page.url:
            print("❌ Captcha / login")
            return

        for _ in range(random.randint(4, 7)):
            page.mouse.wheel(0, random.randint(800, 1200))
            time.sleep(random.uniform(1.2, 2.0))

        items = page.query_selector_all("div[class*='offer']")
        print(f"Znaleziono: {len(items)} ofert")

        browser.close()

if __name__ == "__main__":
    run()

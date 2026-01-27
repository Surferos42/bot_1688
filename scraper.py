from playwright.sync_api import sync_playwright
from playwright_stealth import stealth
import time
import random

URL = "https://s.1688.com/selloffer/offer_search.htm?keywords=usb%20cable"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/119.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            viewport={"width": 1366, "height": 768}
        )

        page = context.new_page()
        stealth(page)

        print("➡️ Otwieram 1688...")
        page.goto(URL, timeout=60000, wait_until="domcontentloaded")

        # ⏱ losowy delay
        time.sleep(random.uniform(3, 6))

        # ❌ captcha / login
        if "login.1688.com" in page.url:
            print("❌ Zablokowani: captcha / login")
            browser.close()
            return

        # 🖱 human-like scroll
        for _ in range(random.randint(4, 7)):
            page.mouse.wheel(0, random.randint(800, 1200))
            time.sleep(random.uniform(1.2, 2.0))

        # 🧱 ODPORNE SELEKTORY
        items = page.query_selector_all("div[class*='offer']")
        print(f"✅ Znaleziono ofert: {len(items)}")

        results = []

        for item in items:
            link_el = item.query_selector(
                "a[href*='detail.1688.com/offer']"
            )
            if not link_el:
                continue

            url = link_el.get_attribute("href")
            title = link_el.inner_text().strip()

            img_el = link_el.query_selector("img")
            img = img_el.get_attribute("src") if img_el else None

            price_el = item.query_selector("span:has-text('¥')")
            price = price_el.inner_text().strip() if price_el else None

            results.append({
                "title": title,
                "price": price,
                "url": url,
                "image": img
            })

        browser.close()

        print("\n📦 WYNIKI (pierwsze 10):\n")
        for r in results[:10]:
            print("🟢", r["title"])
            print("   💰", r["price"])
            print("   🔗", r["url"])
            print()

if __name__ == "__main__":
    run()

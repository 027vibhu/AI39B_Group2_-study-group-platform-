import asyncio
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:5000"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        # Log in as the auto-created admin account
        await page.goto(f"{BASE}/login")
        await page.fill('.sign-in-form input[name="identifier"]', "admin")
        await page.fill('.sign-in-form input[name="password"]', "mingmasherpa")
        await page.click('.sign-in-form button[type="submit"], .sign-in-form input[type="submit"]')
        await page.wait_for_load_state("networkidle")
        print("after login:", page.url)

        # --- PRIVATE room ---
        await page.goto(f"{BASE}/create_room")
        await page.wait_for_load_state("networkidle")
        await page.fill('input[name="room_name"]', "Private CSS Test")
        await page.click('.visibility-card:has-text("Private")')
        await page.screenshot(path="shot_create_private.png")
        await page.click('button.main-btn')
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1500)
        print("private chat url:", page.url)
        await page.screenshot(path="shot_chat_private.png", full_page=False)

        # --- PUBLIC room ---
        await page.goto(f"{BASE}/create_room")
        await page.wait_for_load_state("networkidle")
        await page.fill('input[name="room_name"]', "Public CSS Test")
        await page.click('button.main-btn')
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1500)
        print("public chat url:", page.url)
        await page.screenshot(path="shot_chat_public.png", full_page=False)

        await browser.close()

asyncio.run(main())

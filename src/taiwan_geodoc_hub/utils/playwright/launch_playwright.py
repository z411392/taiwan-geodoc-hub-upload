from contextlib import asynccontextmanager
from playwright.async_api import async_playwright


@asynccontextmanager
async def launch_playwright():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )
        try:
            page = await browser.new_page()
            try:
                yield page
            finally:
                await page.close()
        finally:
            await browser.close()

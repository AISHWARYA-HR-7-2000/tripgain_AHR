import asyncio
from playwright.async_api import async_playwright

async def auto_flight_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.budgetticket.in", timeout=60000)

        # --- Origin ---
        await page.fill("#fromCity", "Bangalore")
        # Wait for autocomplete suggestions and click first
        await page.wait_for_selector(".autocomplete-suggestion", timeout=5000)
        await page.click(".autocomplete-suggestion")

        # --- Destination ---
        await page.fill("#toCity", "Delhi")
        await page.wait_for_selector(".autocomplete-suggestion", timeout=5000)
        await page.click(".autocomplete-suggestion")

        # --- Journey Date ---
        # Directly fill the date in DD/MM/YYYY format
        await page.fill("#departure", "26/10/2025")

        # --- Click Search ---
        await page.click("#searchButton")

        # Wait until flight results load
        await page.click(".fixed-header #searchButton")
        await page.wait_for_selector(".result-card", timeout=15000)  # wait for results


        # Keep browser open to see results
        await asyncio.sleep(10)
        await browser.close()

asyncio.run(auto_flight_search())

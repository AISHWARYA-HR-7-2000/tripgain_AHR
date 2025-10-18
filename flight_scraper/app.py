import json
from datetime import datetime
from playwright.async_api import async_playwright
import asyncio

async def scrape_flights(origin, destination, journey_date):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.budgetticket.in", timeout=60000)

        # --- Origin ---
        await page.fill("#fromCity", origin)
        # Wait for the autocomplete dropdown and select first option
        await page.wait_for_selector(".autocomplete-suggestion")
        await page.click(".autocomplete-suggestion")

        # --- Destination ---
        await page.fill("#toCity", destination)
        await page.wait_for_selector(".autocomplete-suggestion")
        await page.click(".autocomplete-suggestion")

        # --- Journey Date ---
        # If the input allows typing directly:
        await page.fill("#departure", journey_date)

        # --- Click Search ---
        await page.click("#searchButton")

        # Wait until flight results are loaded
        await page.wait_for_selector(".result-card")  # adjust selector based on actual site

        # --- Extract flight data ---
        flights = []
        results = await page.query_selector_all(".result-card")  # adjust selector
        for r in results:
            airline = await r.query_selector_eval(".airline-name", "el => el.textContent") if await r.query_selector(".airline-name") else None
            flight_no = await r.query_selector_eval(".flight-number", "el => el.textContent") if await r.query_selector(".flight-number") else None
            dep_time = await r.query_selector_eval(".departure-time", "el => el.textContent") if await r.query_selector(".departure-time") else None
            arr_time = await r.query_selector_eval(".arrival-time", "el => el.textContent") if await r.query_selector(".arrival-time") else None
            price = await r.query_selector_eval(".price", "el => el.textContent") if await r.query_selector(".price") else None

            flights.append({
                "airline": airline,
                "flight_number": flight_no,
                "departure": dep_time,
                "arrival": arr_time,
                "price": price,
                "origin": origin,
                "destination": destination,
                "searchdatetime": datetime.utcnow().isoformat()
            })

        await browser.close()

        # Save JSON
        with open("flight_results.json", "w", encoding="utf-8") as f:
            json.dump(flights, f, indent=4, ensure_ascii=False)

        print(f"Total flights extracted: {len(flights)}")
        return flights

# Example run
asyncio.run(scrape_flights("Bangalore", "Delhi", "2025-10-20"))

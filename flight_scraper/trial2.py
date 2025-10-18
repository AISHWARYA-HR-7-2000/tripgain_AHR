# flight_search_automation.py

import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def scrape_flights(origin: str, destination: str, journey_date: str):
    flights_data = []
    search_time = datetime.utcnow().isoformat() + "Z"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.budgetticket.in", timeout=60000)

        # Click on flight search tab if required
        await page.click('text="Flights"')  # may be optional depending on site behavior

        # Enter origin
        await page.fill('#fromCity', origin)
        await page.wait_for_timeout(1000)
        await page.keyboard.press("Enter")

        # Enter destination
        await page.fill('#toCity', destination)
        await page.wait_for_timeout(1000)
        await page.keyboard.press("Enter")

        # Select journey date (adjust selector as per site)
        await page.fill('#departureDate', journey_date)
        await page.keyboard.press("Enter")

        # Click on search button
        await page.click('button:has-text("Search Flights")')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(5000)  # wait extra to ensure results are fully loaded

        # Extract flights data — these selectors may vary; inspect site and update
        flight_cards = await page.query_selector_all('.flight-card, .search_result_card')

        for card in flight_cards:
            airline = await card.query_selector_eval('.airline-name', 'el => el.innerText') if await card.query_selector('.airline-name') else ''
            flight_no = await card.query_selector_eval('.flight-number', 'el => el.innerText') if await card.query_selector('.flight-number') else ''
            departure = await card.query_selector_eval('.departure-time', 'el => el.innerText') if await card.query_selector('.departure-time') else ''
            arrival = await card.query_selector_eval('.arrival-time', 'el => el.innerText') if await card.query_selector('.arrival-time') else ''
            price = await card.query_selector_eval('.fare-price', 'el => el.innerText') if await card.query_selector('.fare-price') else ''

            flights_data.append({
                "airline": airline.strip(),
                "flight_number": flight_no.strip(),
                "departure": departure.strip(),
                "arrival": arrival.strip(),
                "price": price.strip(),
                "origin": origin,
                "destination": destination,
                "searchdatetime": search_time
            })

        await browser.close()

    # Save to file
    with open("flight_results.json", "w", encoding="utf-8") as f:
        json.dump(flights_data, f, indent=2, ensure_ascii=False)

    print(f"Total Flights Extracted: {len(flights_data)}")
    return flights_data


# Run directly for testing
if __name__ == "__main__":
    origin = "Bangalore"
    destination = "Delhi"
    journey_date = "2025-10-25"
    asyncio.run(scrape_flights(origin, destination, journey_date))

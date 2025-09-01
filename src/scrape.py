# src/scrape_cards.py
import asyncio
from src.utils import log

async def scrape_cards(page, settings: dict):
    """
    Scrape product cards from an infinite-scroll inventory page.
    Each card contains title, category, ID, cost, details, inventory, modified, weight, composition, etc.
    """

    log("🔎 Starting infinite scroll scraping...")

    products = []

    # --- STEP 1: Find total count from "Showing X of Y products"
    total_selector = "div.text-sm.text-muted-foreground span.font-medium.text-foreground:last-of-type"
    await page.wait_for_selector(total_selector)
    total_count = int(await page.inner_text(total_selector))
    log(f"📦 Expecting {total_count} products...")

    # --- STEP 2: Keep scrolling until we've collected all products
    seen = set()

    while len(products) < total_count:
        # Scroll to bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.5)  # give time for lazy load

        # Select all cards
        cards = await page.locator("div.rounded-lg.border.bg-card").all()

        for card in cards:
            # Get ID (unique)
            product_id = await card.locator("p.text-xs.text-muted-foreground.font-mono").inner_text()
            if product_id in seen:
                continue
            seen.add(product_id)

            title = await card.locator("h3").inner_text()
            category = await card.locator("div.inline-flex").inner_text()

            # Extract details from <dl>
            rows = await card.locator("dl div.flex").all()
            details = {}
            for row in rows:
                key = (await row.locator("dt").inner_text()).rstrip(":")
                value = await row.locator("dd").inner_text()
                details[key] = value

            product = {
                "id": product_id.replace("ID: ", ""),
                "title": title,
                "category": category,
                **details,
            }
            products.append(product)

        log(f"✅ Loaded {len(products)}/{total_count} products so far...")

    log(f"🎉 Scraping finished. Collected {len(products)} products.")
    return products

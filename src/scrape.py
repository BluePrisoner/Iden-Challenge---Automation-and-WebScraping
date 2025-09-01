# src/scrape_cards.py
import asyncio
from src.utils import log

from playwright.async_api import Page

async def scrape_cards(page: Page, selectors: dict, settings: dict):
    """Scrape product cards safely (no strict mode issues)."""

    data = []

    # Each product card
    cards = page.locator("div.rounded-lg.border.bg-card")
    count = await cards.count()

    for i in range(count):
        card = cards.nth(i)

        # ✅ Get the product title (only the text-lg headings)
        title = await card.locator("h3.font-semibold.text-lg").first.inner_text()

        # ✅ Get the SKU (unique <p> with those classes)
        sku = await card.locator("p.text-xs.text-muted-foreground.font-mono").first.inner_text()

        # ✅ Get description if it exists (not all cards may have one)
        description = ""
        desc_locator = card.locator("p.text-sm.text-muted-foreground")
        if await desc_locator.count() > 0:
            description = await desc_locator.first.inner_text()

        data.append({
            "title": title.strip(),
            "sku": sku.strip(),
            "description": description.strip(),
        })

    return data

import asyncio
import pytest
from playwright.async_api import async_playwright

from src.auth import ensure_session
from src.scrape import scrape_cards


@pytest.mark.asyncio
async def test_basic_flow():
    """Minimal smoke test: login, navigate, and scrape at least one row."""
    from src.main import load_config

    settings, selectors = load_config()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)

        # ✅ Unpack context and page
        context, page = await ensure_session(browser, settings, selectors)

        # ✅ Use the existing page, not browser
        #page = await goto_inventory_section(page, settings, selectors)

        data = await scrape_cards(page,selectors, settings)

        assert isinstance(data, list)
        assert all(isinstance(row, dict) for row in data)

        print("\nScraped Products:")
        for product in data:
            print(product)


        await page.pause()

        await browser.close()

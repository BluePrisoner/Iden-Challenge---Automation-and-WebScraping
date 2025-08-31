import asyncio
import pytest
from playwright.async_api import async_playwright

from src.auth import ensure_session
from src.navigate import navigate_to_table
from src.scrape import scrape_table


@pytest.mark.asyncio
async def test_basic_flow():
    """Minimal smoke test: login, navigate, and scrape at least one row."""
    from src.main import load_config

    settings, selectors = load_config()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await ensure_session(browser, settings, selectors)
        page = await context.new_page()

        await navigate_to_table(page, settings, selectors)
        data = await scrape_table(page, selectors, settings)

        assert isinstance(data, list)
        assert all(isinstance(row, dict) for row in data)

        await browser.close()

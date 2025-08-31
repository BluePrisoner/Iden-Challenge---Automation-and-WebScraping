import os
from playwright.async_api import Browser, BrowserContext, Page, TimeoutError
from src.utils import log


async def perform_login(page: Page, settings: dict, selectors: dict):
    """Perform login with username and password using provided selectors."""
    log("Performing login...")

    await page.goto(settings["base_url"], wait_until="networkidle")

    # Wait for username field
    await page.wait_for_selector(selectors["login"]["username"])

    await page.fill(selectors["login"]["username"], settings["username"])
    await page.fill(selectors["login"]["password"], settings["password"])
    await page.click(selectors["login"]["submit"])

    # Wait for successful login indicator (customize selector as needed)
    try:
        await page.wait_for_selector(selectors["login"]["success_indicator"], timeout=10000)
        log("Login successful.")
    except TimeoutError:
        raise RuntimeError("Login failed: success indicator not found.")


async def ensure_session(
    browser: Browser,
    settings: dict,
    selectors: dict,
    force_login: bool = False,
) -> BrowserContext:
    """
    Ensure we have a valid logged-in session.
    If a saved session exists, reuse it.
    Otherwise perform login and save session.
    """
    storage_file = settings["storage_state"]

    # Reuse existing session if possible
    if not force_login and os.path.exists(storage_file):
        log("Reusing existing session...")
        context = await browser.new_context(storage_state=storage_file)
        return context

    # Otherwise perform fresh login
    log("No valid session found, logging in again...")
    context = await browser.new_context()
    page = await context.new_page()
    await perform_login(page, settings, selectors)

    # Save session for reuse
    await context.storage_state(path=storage_file)
    log(f"Session saved to {storage_file}")

    return context




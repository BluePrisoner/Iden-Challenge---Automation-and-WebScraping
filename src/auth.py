import os
import json
from playwright.async_api import Browser, BrowserContext, Page, TimeoutError
from src.utils import log


async def perform_login(page: Page, settings: dict, selectors: dict):
    """Perform login and navigate through the challenge setup."""
    log("Performing login...")

    # Go directly to login page
    login_url = settings["base_url"].rstrip("/") + settings.get("login_path", "")
    await page.goto(login_url, wait_until="networkidle")

    # Wait for username field and fill form
    await page.wait_for_selector(selectors["login"]["username"])
    await page.fill(selectors["login"]["username"], settings["username"])
    await page.fill(selectors["login"]["password"], settings["password"])
    await page.click(selectors["login"]["submit"])

    # Step 1: Launch Challenge (if exists)
    try:
        await page.wait_for_selector(selectors["login"]["launch_challenge"], timeout=5000)
        await page.click(selectors["login"]["launch_challenge"])
        log("Clicked 'Launch Challenge'")
    except TimeoutError:
        log("No 'Launch Challenge' button found — continuing...")

    # Step 2: Start Journey (if exists)
    try:
        await page.wait_for_selector(selectors["login"]["start_journey"], timeout=5000)
        await page.click(selectors["login"]["start_journey"])
        log("Clicked 'Start Journey'")
    except TimeoutError:
        log("No 'Start Journey' button found — continuing...")

    # Step 3: Continue Search
    try:
        await page.wait_for_selector(selectors["login"]["continue_search"], timeout=10000)
        await page.click(selectors["login"]["continue_search"])
        log("Clicked 'Continue Search'")
    except TimeoutError:
        raise RuntimeError("Login failed: 'Continue Search' button not found.")

    # Step 4: Success indicator = Inventory Section
    try:
        await page.wait_for_selector(selectors["login"]["success_indicator"], timeout=10000)
        log("Login successful. 'Inventory Section' button found.")
    except TimeoutError:
        await page.screenshot(path="login_failed.png")
        raise RuntimeError("Login failed: success indicator not found.")


async def ensure_session(
    browser: Browser,
    settings: dict,
    selectors: dict,
    force_login: bool = False,
) -> BrowserContext:
    """
    Ensure we have a valid logged-in session.
    If a saved session exists and is valid JSON, reuse it.
    Otherwise perform login and save session.
    """
    storage_file = settings["storage_state_file"]

    # Try reusing session only if file exists and contains valid JSON
    if not force_login and os.path.exists(storage_file):
        try:
            with open(storage_file, "r", encoding="utf-8") as f:
                json.load(f)  # validate JSON
            log("Reusing existing session...")
            context = await browser.new_context(storage_state=storage_file)
            return context
        except (json.JSONDecodeError, OSError):
            log("Invalid or empty storage_state.json, performing fresh login...")

    # Otherwise perform fresh login
    log("No valid session found, logging in again...")
    context = await browser.new_context()
    page = await context.new_page()
    await perform_login(page, settings, selectors)

    # Save session for reuse
    os.makedirs(os.path.dirname(storage_file), exist_ok=True)
    await context.storage_state(path=storage_file)
    log(f"Session saved to {storage_file}")

    return context

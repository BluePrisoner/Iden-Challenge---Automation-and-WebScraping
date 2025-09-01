import os
import json
from playwright.async_api import Browser, BrowserContext, Page, TimeoutError
from src.utils import log, save_storage_state


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
        await page.wait_for_selector(selectors["login"]["inventory_section"], timeout=10000)
        await page.click(selectors["login"]["inventory_section"])
        log("Clicked 'Inventory Section'")
        log("Login successful. 'Inventory Section' button found.")
    except TimeoutError:
        await page.screenshot(path="login_failed.png")
        raise RuntimeError("Login failed: success indicator not found.")

    # ✅ Capture cookies, localStorage, and sessionStorage for debugging
    cookies = await page.context.cookies()
    local_storage = await page.evaluate("JSON.stringify(localStorage)")
    session_storage = await page.evaluate("JSON.stringify(sessionStorage)")

    # Print for debug
    print("Cookies:", json.dumps(cookies, indent=2))
    print("LocalStorage:", local_storage)
    print("SessionStorage:", session_storage)

    return {
        "cookies": cookies,
        "localStorage": json.loads(local_storage),
        "sessionStorage": json.loads(session_storage),
    }


async def ensure_session(
    browser: Browser,
    settings: dict,
    selectors: dict,
    force_login: bool = True,
) -> tuple[BrowserContext, Page]:
    """
    Ensure a logged-in session is available.
    Always returns the same Page so no extra tabs are opened.
    """
    storage_file = settings["storage_state_file"]

    if not force_login and os.path.exists(storage_file):
        try:
            with open(storage_file, "r", encoding="utf-8") as f:
                json.load(f)
            log("Reusing existing session...")

            context = await browser.new_context(storage_state=storage_file)
            page = await context.new_page()
            await page.goto(settings["base_url"], wait_until="domcontentloaded")
            return context, page
        except (json.JSONDecodeError, OSError):
            log("Invalid session, will re-login...")

    # Fresh login
    log("Performing fresh login...")
    context = await browser.new_context()
    page = await context.new_page()

    await perform_login(page, settings, selectors)

    # Wait for app fully loaded
    await page.wait_for_load_state("networkidle")

    # Save state
    os.makedirs(os.path.dirname(storage_file), exist_ok=True)
    await save_storage_state(context, page, storage_file)
    log(f"Session saved to {storage_file}")

    return context, page

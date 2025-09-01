from src.utils import log, wait_for

async def goto_inventory_section(page, settings: dict, selectors: dict):
    """
    Navigate to Inventory Section using existing authenticated session.
    Assumes session was restored by Playwright context (ensure_session).
    """
    log("📂 Using existing session (no manual injection)")

    # Go directly to base_url (session already restored via storage_state.json)
    await page.goto(settings["base_url"], wait_until="domcontentloaded")

    # Wait for and click "Inventory Section"
    await wait_for(page.locator(selectors["login"]["inventory_section"]))
    await page.click(selectors["login"]["inventory_section"])
    log("➡️ Clicked 'Inventory Section'")

    return page

from utils import log, wait_for


async def navigate_to_table(page, settings: dict, selectors: dict):
    """
    Navigate through the hidden path:
    Start Journey → Continue Search → Inventory Section → Show Product Table
    """
    log("🧭 Navigating to product table...")

    # Start Journey
    await wait_for(page.locator(selectors["navigation"]["start_journey"]))
    await page.click(selectors["navigation"]["start_journey"])
    log("➡️ Clicked 'Start Journey'")

    # Continue Search
    await wait_for(page.locator(selectors["navigation"]["continue_search"]))
    await page.click(selectors["navigation"]["continue_search"])
    log("➡️ Clicked 'Continue Search'")

    # Inventory Section
    await wait_for(page.locator(selectors["navigation"]["inventory_section"]))
    await page.click(selectors["navigation"]["inventory_section"])
    log("➡️ Clicked 'Inventory Section'")

    # Show Product Table
    await wait_for(page.locator(selectors["navigation"]["show_product_table"]))
    await page.click(selectors["navigation"]["show_product_table"])
    log("➡️ Clicked 'Show Product Table'")

    # Wait for table container
    await wait_for(page.locator(selectors["table"]["container"]))
    log("📄 Product table is visible now")




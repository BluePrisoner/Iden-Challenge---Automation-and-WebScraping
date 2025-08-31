from utils import log, wait_for


async def scrape_table(page, selectors: dict, settings: dict):
    """
    Scrape all product data from the table, handling pagination or lazy-loading.
    Returns a list of dictionaries, one per row.
    """
    log("🔍 Scraping product table...")

    all_rows = []

    while True:
        # Wait for rows to be visible
        await wait_for(page.locator(selectors["table"]["rows"]))

        # Extract headers
        headers = await page.locator(selectors["table"]["headers"]).all_inner_texts()
        headers = [h.strip() for h in headers]

        # Extract rows
        row_elements = await page.locator(selectors["table"]["rows"]).all()
        for row in row_elements:
            cells = await row.locator(selectors["table"]["cells"]).all_inner_texts()
            cells = [c.strip() for c in cells]
            row_data = dict(zip(headers, cells))
            all_rows.append(row_data)

        log(f"📦 Collected {len(all_rows)} rows so far...")

        # Handle pagination based on strategy
        pagination_type = settings.get("pagination", "next_button")

        if pagination_type == "next_button":
            next_button = page.locator(selectors["pagination"]["next_button"])
            if await next_button.is_enabled():
                await next_button.click()
                await page.wait_for_load_state("networkidle")
                continue
            else:
                break

        elif pagination_type == "load_more":
            load_more_btn = page.locator(selectors["pagination"]["load_more"])
            if await load_more_btn.is_visible():
                await load_more_btn.click()
                await page.wait_for_load_state("networkidle")
                continue
            else:
                break

        elif pagination_type == "infinite_scroll":
            prev_count = len(all_rows)
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(1500)
            new_count = len(
                await page.locator(selectors["table"]["rows"]).all_inner_texts()
            )
            if new_count > prev_count:
                continue
            else:
                break
        else:
            log(f"⚠️ Unknown pagination type: {pagination_type}, stopping scrape.")
            break

    log(f"✅ Finished scraping. Total rows collected: {len(all_rows)}")
    return all_rows




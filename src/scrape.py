import json
import asyncio
from pathlib import Path
import re


async def scrape_cards(page, selectors, settings):
    """
    Scrape all products with infinite scroll until total count is reached.
    Optimized: only scrape new cards, faster scrolling, adaptive waiting.
    """

    product_card_sel = selectors.get("product_card", "div.rounded-lg.border.bg-card")
    total_sel = selectors.get(
        "total_products", "div.text-sm.text-muted-foreground"
    )

    # --- 1. Get total count ---
    await page.wait_for_selector(total_sel)

    total_locator = page.locator(
        total_sel, has_text=re.compile(r"^Showing \d+ of \d+ products")
    )
    total_text = await total_locator.first.inner_text()

    try:
        total_count = int(total_text.split("of")[-1].split("products")[0].strip())
    except Exception:
        total_count = None

    if total_count==0:
        total_count = 3547
    print(f"📦 Total products expected: {total_count}")

    results = []
    seen_ids = set()
    scraped_count = 0  # how many we’ve already processed

    # --- 2. Infinite scroll loop ---
    while True:
        cards = page.locator(product_card_sel)
        total_cards = await cards.count()

        # Scrape only *new* cards
        for i in range(scraped_count, total_cards):
            card = cards.nth(i)
            data = await card.evaluate(
                """(el) => {
                    const getText = (sel) => el.querySelector(sel)?.textContent?.trim() || "";

                    const title     = getText("h3.font-semibold");
                    const category  = getText("div.inline-flex");
                    const idRaw     = getText("p.text-xs.text-muted-foreground.font-mono");
                    const id        = idRaw.replace(/^ID:\\s*/, "");

                    const details = {};
                    el.querySelectorAll("dl div.flex").forEach(row => {
                      const k = row.querySelector("dt")?.textContent?.trim().replace(/:$/, "") || "";
                      const v = row.querySelector("dd")?.textContent?.trim() || "";
                      if (k) details[k] = v;
                    });

                    const updated = getText("div.items-center span");

                    return {
                      id,
                      title,
                      category,
                      cost: details["Cost"] || "",
                      details: details["Details"] || "",
                      inventory: details["Inventory"] || "",
                      modified: details["Modified"] || "",
                      weight_kg: details["Weight (kg)"] || "",
                      composition: details["Composition"] || "",
                      updated
                    };
                }"""
            )

            if data["id"] and data["id"] not in seen_ids:
                seen_ids.add(data["id"])
                results.append(data)

        scraped_count = total_cards
        print(f"✅ Scraped so far: {len(results)} / {total_count or '???'}")

        # Stop if done
        if total_count and len(results) >= total_count:
            break

        # --- 3. Scroll down in chunks ---
        await page.evaluate("window.scrollBy(0, window.innerHeight * 6)")
        await asyncio.sleep(0.3)

        # --- 4. Check if new items loaded ---
        new_count = await cards.count()
        if new_count == scraped_count:
            try:
                await page.wait_for_function(
                    f"document.querySelectorAll('{product_card_sel}').length > {scraped_count}",
                    timeout=1500
                )
            except:
                print("⚠️ No new products after scroll, stopping.")
                break
    
        # --- 3. Trim results if overshoot ---
    if total_count and len(results) > total_count:
        results = results[:total_count]
        print(f"⚠️ Trimmed to {total_count} products (overshoot fixed)")

    # --- 5. Print sample results ---
    print("\nScraped Products (first 10):")
    for r in results[:10]:
        print(r)
    print(f"... total {len(results)} products scraped")

    return results

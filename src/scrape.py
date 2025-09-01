# src/scrape_cards.py
import asyncio
from src.utils import log

from playwright.async_api import Page

import json
from pathlib import Path

async def scrape_cards(page, selectors, settings):
    """
    Scrape visible product cards and return a list of dicts.
    - Scopes all queries inside each card element (no strict-mode errors).
    - Prints results to terminal.
    - Writes to settings['output_file'] if provided.
    """

    # Fallback CSS for the card if selectors file doesn't provide one
    product_card_sel = selectors.get("product_card", "div.rounded-lg.border.bg-card")

    # Wait for at least one card to be present
    await page.wait_for_selector(product_card_sel)

    cards = page.locator(product_card_sel)
    count = await cards.count()
    results = []

    for i in range(count):
        card = cards.nth(i)

        # Extract purely relative to the card node (no page-wide matches)
        data = await card.evaluate(
            """(el) => {
                const getText = (sel) => el.querySelector(sel)?.textContent?.trim() || "";

                const title     = getText("h3.font-semibold");
                const category  = getText("div.inline-flex");
                const idRaw     = getText("p.text-xs.text-muted-foreground.font-mono"); // e.g. "ID: 0"
                const id        = idRaw.replace(/^ID:\\s*/, "");

                // Collect all <dt>/<dd> pairs inside this card
                const details = {};
                el.querySelectorAll("dl div.flex").forEach(row => {
                  const k = row.querySelector("dt")?.textContent?.trim().replace(/:$/, "") || "";
                  const v = row.querySelector("dd")?.textContent?.trim() || "";
                  if (k) details[k] = v;
                });

                const updated = getText("div.items-center span");

                // Normalize keys (no nested object, as requested)
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

        results.append(data)

    # Print to terminal
    print("\nScraped Products:")
    for r in results:
        print(r)

    # Save to JSON if configured
    output_file = settings.get("output_file")
    if output_file:
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    return results

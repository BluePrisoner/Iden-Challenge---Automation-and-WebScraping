import argparse
import asyncio
import yaml
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from typing import Optional
from pathlib import Path
import json

from src.auth import ensure_session
from src.scrape import scrape_cards
from src.utils import log, save_storage_state


def load_config():
    
    with open("config/settings.yaml", "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)

    with open("config/selectors.yaml", "r", encoding="utf-8") as f:
        selectors = yaml.safe_load(f)

   
    load_dotenv()

    settings["username"] = os.getenv("APP_USERNAME")
    settings["password"] = os.getenv("APP_PASSWORD")
    settings["base_url"] = os.getenv("BASE_URL")


    return settings, selectors


async def main(force_login: bool = True, output_file: Optional[str] = None):

    settings, selectors = load_config()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context, page = await ensure_session(
            browser, settings, selectors, force_login=True
        )

        # Scrape product data
        products = await scrape_cards(page,selectors, settings)

        
        output_file = settings.get("output_file")
        if output_file:
            out_path = Path(output_file)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(products, f, indent=2, ensure_ascii=False)

        log(f"Extraction complete. Saved {len(products)} products to {output_file}")

        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Playwright Product Scraper")
    parser.add_argument(
        "--force-login",
        action="store_true",
        help="Force re-login even if storage state exists",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom output JSON file path",
    )
    args = parser.parse_args()

    asyncio.run(main(force_login=args.force_login, output_file=args.output))

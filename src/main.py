import argparse
import asyncio
import yaml
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from typing import Optional

from src.auth import ensure_session
from src.navigate import navigate_to_table
from src.scrape import scrape_table
from src.export import export_to_json
from src.utils import log


def load_config():
    """Load settings and selectors from YAML + environment variables."""
    with open("config/settings.yaml", "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)

    with open("config/selectors.yaml", "r", encoding="utf-8") as f:
        selectors = yaml.safe_load(f)

    # Load .env
    load_dotenv()

    settings["username"] = os.getenv("APP_USERNAME")
    settings["password"] = os.getenv("APP_PASSWORD")
    settings["base_url"] = os.getenv("BASE_URL", settings["base_url"])
    settings["github_repo_url"] = os.getenv("GITHUB_REPO_URL")

    return settings, selectors


async def main(force_login: bool = False, output_file: Optional[str] = None):

    settings, selectors = load_config()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await ensure_session(
            browser, settings, selectors, force_login=force_login
        )

        page = await context.new_page()

        # Navigate to product table
        await navigate_to_table(page, settings, selectors)

        # Scrape product data
        products = await scrape_table(page, selectors, settings)

        # Export results
        output_path = output_file or settings["output_file"]
        export_to_json(products, output_path)

        log(f"Extraction complete. Saved {len(products)} products to {output_path}")

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

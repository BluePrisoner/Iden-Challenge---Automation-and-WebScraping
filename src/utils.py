import asyncio
from playwright.async_api import Locator


def log(message: str):
    """Simple logger with consistent formatting."""
    print(f"[Scraper] {message}")


async def wait_for(locator: Locator, timeout: int = 10000):
    """
    Wait until a locator is visible and enabled before continuing.
    Raises TimeoutError if not found within `timeout` ms.
    """
    try:
        await locator.wait_for(state="visible", timeout=timeout)
        await locator.wait_for(state="attached", timeout=timeout)
    except Exception as e:
        log(f"⚠️ Timeout waiting for element: {e}")
        raise


async def retry(coro_func, retries: int = 3, delay: float = 1.0):
    """
    Retry an async coroutine function a few times with delay in case of flakiness.
    """
    for attempt in range(1, retries + 1):
        try:
            return await coro_func()
        except Exception as e:
            log(f"⚠️ Attempt {attempt} failed: {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                raise

# utils/storage_helper.py
import json
import os


async def save_storage_state(context, page, storage_file: str):
    """Save cookies, localStorage, and sessionStorage into a single JSON file."""
    os.makedirs(os.path.dirname(storage_file), exist_ok=True)

    # Save base Playwright storage (cookies + localStorage)
    await context.storage_state(path=storage_file)

    # Grab sessionStorage from the logged-in page
    session_storage = await page.evaluate("JSON.stringify(sessionStorage)")

    # Merge sessionStorage into the saved file
    with open(storage_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["sessionStorage"] = json.loads(session_storage)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    print(f"✅ Storage state (including sessionStorage) saved at {storage_file}")

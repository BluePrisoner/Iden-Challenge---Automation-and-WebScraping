import asyncio
from playwright.async_api import Locator


def log(message: str):
    print(f"[Scraper] {message}")


async def wait_for(locator: Locator, timeout: int = 10000):
    try:
        await locator.wait_for(state="visible", timeout=timeout)
        await locator.wait_for(state="attached", timeout=timeout)
    except Exception as e:
        log(f"Timeout waiting for element: {e}")
        raise


async def retry(coro_func, retries: int = 3, delay: float = 1.0):

    for attempt in range(1, retries + 1):
        try:
            return await coro_func()
        except Exception as e:
            log(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                raise

# utils/storage_helper.py
import json
import os


async def save_storage_state(context, page, storage_file: str):
    
    os.makedirs(os.path.dirname(storage_file), exist_ok=True)

    await context.storage_state(path=storage_file)

    session_storage = await page.evaluate("JSON.stringify(sessionStorage)")

    # Merging sessionStorage into the saved file
    with open(storage_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["sessionStorage"] = json.loads(session_storage)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    print(f"Storage state (including sessionStorage) saved at {storage_file}")

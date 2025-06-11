import random
from typing import Any, List
from time import sleep
from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    Locator,
    Request,
)
from src.my_types import RobotTaskType, BrowserWorkerSignals

# from src.robot import selector_constants as selectors
import sys, traceback

MIN = 60_000

SELECTORS = {
    "root": 'div[data-type="vscroller"]',
    "container": 'div[data-type="container"]',
    # "ServerTextArea": 'div[data-mcomponent="ServerTextArea"]',
    "product": '> div[data-mcomponent="ServerTextArea"]:nth-of-type(3)',
    "product_menu_button": 'div[data-client-focused-component="true"]',
    "bottom_sheet": 'div[role="presentation"]',
}


def share_lasted_product(
    page: Page, task: RobotTaskType, settings: dict, signals: BrowserWorkerSignals
):
    listing_id_url = "https://www.facebook.com/marketplace/selling/?listing_id"

    log_prefix = f"[Task {task.user_info.username} - do_launch_browser]"
    progress: List[int] = [0, 4]  # current, total

    def emit_progress_update(message: str):
        progress[0] += 1
        signals.task_progress_signal.emit(message, [progress[0], progress[1]])
        print(f"{log_prefix} Progress: {progress[0]}/{progress[1]} - {message}")

    try:
        page.goto(listing_id_url, timeout=MIN)
        root_locators = page.locator(SELECTORS["root"])
        container_locators = root_locators.first.locator(SELECTORS["container"])
        product_locators = container_locators.filter(
            has=page.locator(SELECTORS["product"])
        )
        product_locators.first.click()
        page.wait_for_url(lambda new_url: new_url != listing_id_url, timeout=MIN)
        if page.url == listing_id_url:
            raise RuntimeError("page.url == listing_id_url")

        ellipsis_locators = page.locator(SELECTORS["product_menu_button"])
        ellipsis_locators.first.click()
        bottom_sheet_locator = (
            page.locator(SELECTORS["bottom_sheet"])
            .filter(has=page.locator(":visible").and_(":enabled"))
            .first
        )
        bottom_sheet_locator.highlight()

        # bottom_sheet_locators

        print("Wait for close")
        # page.wait_for_event("close", timeout=0)

        return True
    except PlaywrightTimeoutError as e:
        # TODO emit signal
        return except_handle(e)
    except RuntimeError as e:
        # TODO emit signal
        return except_handle(e)
    except Exception as e:
        ##TODO emit signal
        return except_handle(e)
    finally:
        page.wait_for_event("close", timeout=0)


def except_handle(e):
    error_type = type(e).__name__
    error_message = str(e)
    full_traceback = traceback.format_exc()

    print(
        f"ERROR: A general error occurred during task execution:",
        file=sys.stderr,
    )
    print(f"  Error Type: {error_type}", file=sys.stderr)
    print(f"  Message: {error_message}", file=sys.stderr)
    print(f"  Traceback Details:\n{full_traceback}", file=sys.stderr)
    return False

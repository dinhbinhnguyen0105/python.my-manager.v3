import random
from typing import Any, List, Optional, Callable
from time import sleep
from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    Locator,
)
from src.my_types import RobotTaskType, BrowserWorkerSignals

# from src.robot import selector_constants as selectors
import sys, traceback

MIN = 60_000

SELECTORS = {
    "root": 'div[data-type="vscroller"]',
    "container": 'div[data-type="container"]',
    "product": '> div[data-mcomponent="ServerTextArea"]:nth-of-type(3)',
    "product_menu_button": 'div[role="button"][data-focusable="true"]',
    "bottom_sheet": 'div[role="presentation"]',
    "fixed_top": "div.fixed-container.top",
    "button": "div[role='button']",
}


def share_latest_product(
    page: Page, task: RobotTaskType, settings: dict, signals: BrowserWorkerSignals
):
    log_prefix = f"[Task {task.user_info.username} - do_launch_browser]"
    progress: List[int] = [0, 4]  # current, total

    try:
        # click vào sản phẩm mới nhất trong list sản phẩm
        product_url = goto_product_details(
            page=page,
            task=task,
            settings=settings,
            signals=signals,
        )
        goto_more_place(
            product_url=product_url,
            page=page,
            task=task,
            signals=signals,
        )

        print("Wait for close")
        page.wait_for_event("close", timeout=0)
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


def goto_product_details(
    page: Page,
    task: RobotTaskType,
    settings: dict,
    signals: BrowserWorkerSignals,
) -> str:
    progress: List[int] = [0, 0]
    log_prefix = f"[Task {task.user_info.username} - do_discussion]"

    def emit_progress_update(message: str):
        progress[0] += 1
        signals.task_progress_signal.emit(message, [progress[0], progress[1]])
        print(f"{log_prefix} Progress: {progress[0]}/{progress[1]} - {message}")

    progress[1] = 10
    emit_progress_update(f"Estimated total steps: {progress[1]}")

    listing_id_url = "https://www.facebook.com/marketplace/selling/?listing_id"
    try:
        page.goto(listing_id_url, wait_until="domcontentloaded", timeout=MIN)
        emit_progress_update(
            "Successfully navigated to listing_id page.",
            [progress[0], progress[1]],
        )
    except PlaywrightTimeoutError as e:
        emit_progress_update(
            "ERROR: Timeout while navigating to listing_id page.",
            [progress[0], progress[1]],
        )
        if settings.get("raw_proxy"):
            signals.proxy_not_ready_signal.emit(task, settings.get("raw_proxy"))
        return False

    emit_progress_update("Checking page language.")
    page_language = page.locator("html").get_attribute("lang")
    signals.task_progress_signal.emit(
        f"Detected page language: '{page_language}'.", [progress[0], progress[1]]
    )
    if page_language != "en":
        signals.task_progress_signal.emit(
            "WARNING: Page language is not English. Language conversion required.",
            [progress[0], progress[1]],
        )
        signals.failed_signal.emit(
            task,
            "Page language conversion to English required.",
            settings.get("raw_proxy", None),
        )
        return False

    # TODO emit signals

    root_locators = page.locator(SELECTORS["root"])
    container_locators = root_locators.first.locator(SELECTORS["container"])
    product_locators = container_locators.filter(
        has=page.locator('> div[data-mcomponent="ServerTextArea"]:nth-of-type(3)')
    )
    product = product_locators.nth(1)
    product.evaluate("elm => elm.click();")

    # chờ page được chuyển hướng tới chi tiết sản phẩm
    page.wait_for_url(lambda new_url: new_url != listing_id_url, timeout=MIN)
    if page.url == listing_id_url:
        raise RuntimeError("page.url == listing_id_url")
    return page.url


def goto_more_place(
    product_url: str,
    page: Page,
    task: RobotTaskType,
    signals: BrowserWorkerSignals,
):
    progress: List[int] = [0, 0]
    log_prefix = f"[Task {task.user_info.username} - do_discussion]"

    def emit_progress_update(message: str):
        progress[0] += 1
        signals.task_progress_signal.emit(message, [progress[0], progress[1]])
        print(f"{log_prefix} Progress: {progress[0]}/{progress[1]} - {message}")

    if product_url != page.url:
        page.goto(product_url, wait_until="domcontentloaded", timeout=MIN)
    # click vào nut menu
    edit_btn_locators = page.locator("[aria-label]")
    count = edit_btn_locators.count()
    edit_btn_locator: Optional[Locator] = None
    for i in range(count):
        edit_btn_locator = edit_btn_locators.nth(i)
        label = edit_btn_locator.get_attribute("aria-label")
        if label and label.lower() == "edit":
            if edit_btn_locator.is_visible() and edit_btn_locator.is_enabled():
                break
            else:
                edit_btn_locator = None
    if not edit_btn_locator:
        raise RuntimeError("Invalid edit button")
    button_container_locators = edit_btn_locator.first.locator("..")
    product_menu_locator = button_container_locators.first.locator(
        SELECTORS["product_menu_button"]
    )
    product_menu_locator.nth(1).evaluate("elm => elm.click();")
    page.wait_for_selector(SELECTORS["bottom_sheet"], timeout=30000)
    bottom_sheet_locators = page.locator(SELECTORS["bottom_sheet"])
    bottom_sheet_locator: Optional[Locator] = None
    count = bottom_sheet_locators.count()
    for i in range(count):
        if (
            bottom_sheet_locators.nth(i).is_visible()
            and bottom_sheet_locators.nth(i).is_enabled()
        ):
            bottom_sheet_locator = bottom_sheet_locators.nth(i)
            break
    if not bottom_sheet_locator:
        raise RuntimeError("Invalid bottom sheet")

    # click vào nut list list in more place
    list_more_button_locators: Optional[Locator] = None
    page.wait_for_selector(SELECTORS["button"], timeout=30000)
    sheet_button_locators = bottom_sheet_locator.locator(SELECTORS["button"])
    count = sheet_button_locators.count()
    for i in range(count):
        btn = sheet_button_locators.nth(i)
        text = btn.text_content()
        if text and "more places" in text.strip().lower():
            list_more_button_locators = btn
            break
    if not list_more_button_locators:
        raise RuntimeError("Invalid list in more place")
    list_more_button_locators.first.evaluate("elm => elm.click();")


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
